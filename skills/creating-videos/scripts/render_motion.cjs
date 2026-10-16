#!/usr/bin/env node
'use strict';
// Original local composition renderer. No hosted APIs or remote asset loading.
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const { createRequire } = require('node:module');

async function main() {
  const args = process.argv.slice(2);
  if (!args.length || args.includes('--help')) {
    console.log('node render_motion.cjs index.html --output pilot.mp4 [--ffmpeg PATH] [--width N --height N --fps N --duration S] [--config design.json] [--stills-only] [--overwrite]');
    return;
  }
  const input = path.resolve(args.shift()), opts = {};
  const flags = new Set(['stills-only', 'overwrite']);
  const values = new Set(['output', 'ffmpeg', 'width', 'height', 'fps', 'duration', 'config']);
  while (args.length) {
    const key = args.shift().replace(/^--/, '');
    if (flags.has(key)) opts[key] = true;
    else if (values.has(key) && args.length) opts[key] = args.shift();
    else throw new Error(`Unknown or incomplete option: ${key}`);
  }
  if (!opts.output) throw new Error('--output is required');
  const output = path.resolve(opts.output);
  if (path.extname(output).toLowerCase() !== '.mp4') throw new Error('Output must end in .mp4');
  if (!opts.overwrite && await fs.stat(output).catch(() => null)) throw new Error('Output exists; use another name or --overwrite');
  const root = await fs.realpath(path.dirname(input));
  const entry = await fs.realpath(input);
  const config = opts.config ? JSON.parse(await fs.readFile(path.resolve(opts.config), 'utf8')) : {};
  const reviewDir = path.join(path.dirname(output), `${path.basename(output, '.mp4')}-review`);
  await fs.mkdir(reviewDir, { recursive: true });
  const reportPath = path.join(reviewDir, 'review.json');
  const report = { source: entry, output, status: 'pending', creative_review: 'pending', audio: 'silent visual render; finish sound with the editing workflow', errors: [] };
  let browser, encoder, server;
  try {
    let chromium, playwrightVersion;
    for (const base of [path.dirname(entry), process.cwd(), __dirname]) {
      try {
        const localRequire = createRequire(path.join(base, 'package.json'));
        ({ chromium } = localRequire('playwright'));
        playwrightVersion = localRequire('playwright/package.json').version;
        break;
      } catch { /* Try the next explicit project/tool location. */ }
    }
    if (!chromium) throw new Error('Install the free local render dependency in the project: npm install --save-exact playwright; npx playwright install chromium');
    const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json', '.mp4': 'video/mp4' };
    server = http.createServer(async (req, res) => {
      try {
        const requestPath = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
        const file = await fs.realpath(path.resolve(root, `.${requestPath}`));
        const relative = path.relative(root, file);
        if (relative.startsWith('..') || path.isAbsolute(relative) || relative.split(path.sep).some(p => p.startsWith('.'))) throw new Error('Outside composition assets');
        res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' });
        res.end(await fs.readFile(file));
      } catch { res.writeHead(404); res.end('Not found'); }
    });
    server.listen(0, '127.0.0.1');
    await once(server, 'listening');
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1, serviceWorkers: 'block' });
    const errors = [];
    await context.route('**/*', route => {
      const url = route.request().url();
      if (new URL(url).origin === origin || /^(data:|blob:)/.test(url)) return route.continue();
      errors.push(`Remote request blocked: ${url}`);
      return route.abort();
    });
    // Compositions are local authoring projects. Remote WebSockets are blocked too.
    if (typeof context.routeWebSocket === 'function') await context.routeWebSocket('**/*', ws => { errors.push(`WebSocket blocked: ${ws.url()}`); ws.close(); });
    await context.addInitScript({ content: `window.__MOTION_CAPTURE__=true; window.MOTION_CONFIG=${JSON.stringify(config)};` });
    const page = await context.newPage();
    page.on('pageerror', err => errors.push(err.message));
    page.on('response', response => { if (response.status() >= 400) errors.push(`Asset HTTP ${response.status()}: ${response.url()}`); });
    await page.goto(`${origin}/${encodeURIComponent(path.basename(entry))}`, { waitUntil: 'load' });
    const meta = await page.evaluate(async () => {
      await window.motionReady;
      await document.fonts.ready;
      await Promise.all([...document.images].map(image => image.decode()));
      if (typeof window.renderFrame !== 'function') throw new Error('Composition must expose window.renderFrame(seconds, viewport)');
      if (!window.MOTION_META) throw new Error('Composition must expose window.MOTION_META');
      return window.MOTION_META;
    });
    const width = Number(opts.width ?? meta.width), height = Number(opts.height ?? meta.height);
    const fps = Number(opts.fps ?? meta.fps), duration = Number(opts.duration ?? meta.duration);
    if (![width, height].every(n => Number.isInteger(n) && n > 0 && n % 2 === 0 && n <= 7680)) throw new Error('Width/height must be positive even integers up to 7680');
    if (!Number.isInteger(fps) || fps < 1 || fps > 120 || !Number.isFinite(duration) || duration <= 0) throw new Error('Invalid fps or duration');
    if (Number.isFinite(meta.duration) && duration > meta.duration) throw new Error('Duration exceeds the authored composition; extend its motion timeline first');
    const frameCount = Math.round(duration * fps);
    if (frameCount < 1 || Math.abs(frameCount / fps - duration) > 1e-6) throw new Error('Duration must land on the frame grid');
    await page.setViewportSize({ width, height });
    const events = (meta.events || []).map(event => {
      const seconds = event.seconds ?? event.frame / meta.fps;
      if (!Number.isFinite(seconds) || seconds < 0) throw new Error('Invalid sound/event time in MOTION_META');
      const frame = Math.round(seconds * fps);
      return { ...event, frame, seconds: frame / fps };
    }).filter(event => event.frame < frameCount);
    Object.assign(report, { width, height, fps, duration, frame_count: frameCount, events });
    const assertHealthy = () => { if (errors.length) throw new Error([...new Set(errors)].join('\n')); };
    const frame = async seconds => {
      await page.evaluate(async ({ seconds, width, height }) => {
        await window.renderFrame(seconds, { width, height });
        await document.fonts.ready;
        if (document.getAnimations().some(a => a.playState === 'running')) throw new Error('Pause CSS/WAAPI animations and seek them explicitly before capture');
      }, { seconds, width, height });
      assertHealthy();
      return page.screenshot({ type: 'png' });
    };
    const samples = new Set([0, frameCount - 1, Math.floor(frameCount / 2)]);
    for (const seconds of meta.reviewTimes || []) {
      if (Number.isFinite(seconds) && seconds >= 0 && seconds < duration) samples.add(Math.round(seconds * fps));
    }
    const sampleFrames = [...samples].filter(f => f < frameCount).sort((a, b) => a - b);
    const hashes = new Map();
    report.snapshots = [];
    for (const index of sampleFrames) {
      const bytes = await frame(index / fps), name = `frame-${String(index).padStart(6, '0')}.png`;
      hashes.set(index, crypto.createHash('sha256').update(bytes).digest('hex'));
      await fs.writeFile(path.join(reviewDir, name), bytes);
      report.snapshots.push({ frame: index, seconds: index / fps, file: name });
    }
    // Reverse seeks expose accumulated state, live clocks, and unseeded drawing.
    for (const index of [...sampleFrames].reverse()) {
      const bytes = await frame(index / fps);
      if (crypto.createHash('sha256').update(bytes).digest('hex') !== hashes.get(index)) throw new Error(`Non-deterministic render at frame ${index}`);
    }
    report.reverse_seek_check = 'passed';
    if (!opts['stills-only']) {
      const partial = path.join(path.dirname(output), `${path.basename(output, '.mp4')}.${process.pid}.partial.mp4`);
      const ffmpeg = opts.ffmpeg || 'ffmpeg';
      encoder = spawn(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-vcodec', 'png', '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', partial], { stdio: ['pipe', 'ignore', 'pipe'] });
      let stderr = '', encoderError;
      encoder.stderr.on('data', chunk => { stderr = (stderr + chunk).slice(-12000); });
      encoder.on('error', err => { encoderError = err; });
      encoder.stdin.on('error', err => { encoderError = err; });
      const completion = new Promise(resolve => encoder.on('close', code => resolve(code)));
      for (let index = 0; index < frameCount; index++) {
        if (encoderError || encoder.exitCode !== null) throw new Error(`FFmpeg stopped: ${encoderError?.message || stderr}`);
        const bytes = await frame(index / fps);
        if (!encoder.stdin.write(bytes)) await Promise.race([once(encoder.stdin, 'drain'), completion.then(() => { throw new Error(`FFmpeg stopped: ${stderr}`); })]);
        if (index % fps === 0) console.log(`Rendered ${index}/${frameCount} frames`);
      }
      encoder.stdin.end();
      const code = await completion;
      if (code !== 0 || encoderError) throw new Error(`FFmpeg failed: ${encoderError?.message || stderr}`);
      assertHealthy();
      await fs.rename(partial, output);
    }
    report.status = opts['stills-only'] ? 'snapshots_ready' : 'rendered';
    report.dependencies = { node: process.version, playwright: playwrightVersion, chromium: browser.version() };
    console.log(`${report.status}: ${opts['stills-only'] ? reviewDir : output}\nReview: ${reportPath}\nCreative and sound review still required.`);
  } catch (err) {
    report.status = 'failed'; report.errors.push(err.message); throw err;
  } finally {
    if (encoder && encoder.exitCode === null) encoder.kill();
    await browser?.close();
    await new Promise(resolve => server?.listening ? server.close(resolve) : resolve());
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
  }
}
main().catch(err => { console.error(err.message); process.exitCode = 1; });
