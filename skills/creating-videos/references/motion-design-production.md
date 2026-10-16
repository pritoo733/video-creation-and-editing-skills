# Produce an original motion-design film

Use this route for a launch film, visual explainer, brand animation, or social video whose main material is typography, vector artwork, data, or a real product interface. No camera footage is needed when the visual concept can be authored truthfully in code. Choose a different route when genuine people, places, captured behavior, or documentary evidence are central to the story.

The lightweight automatic-free renderer offers four useful diagram layouts. It is not the default for a brief asking for an elaborate motion-design film. For that request, author a custom composition with this guide and the [HyperFrames local workflow](hyperframes-local-workflow.md), or the included independent HTML renderer below. Both can run locally without paid generation APIs; the user's LLM usage and hardware are separate costs.

## Direct the film before animating it

When a visual direction is not yet established, use [the reference library](reference-library-workflow.md) to retrieve relevant public prompts and examples. Extract their motion mechanisms, adapt them into a complete production prompt for this subject, and retain source/creator links. Avoid restarting an approved treatment merely to follow a fashionable reference.

Choose a concrete audience, viewer takeaway, and visual idea. Write a treatment specific to the subject: typography, a small palette, texture, framing, motion behavior, and sound character. For a product, inspect its actual interface and assets; plan a real action and its result. Code-generated artwork is appropriate for an abstract idea, but it must not masquerade as a working feature or captured evidence.

Design the opening as a finished composition with something worth seeing immediately. Empty logo padding, generic promises, and a slow title reveal rarely explain the subject. A tutorial may need a calmer introduction; preserve the user's intended pacing.

Use the [visual beat sheet](../../../templates/visual-beat-sheet.md) to plan what changes in each beat and what survives into the next. A shared object might change its role: an input becomes a connector, the connector forms a diagram, and the diagram opens into a real result. Repeated objects are useful when their visible state evolves with the idea. This differs from holding one unchanged background while replacing headings. A continuous authored scene can span several beats; review its changing states rather than inventing separate source IDs to satisfy montage checks.

Give each handoff a reason: a matching shape, an object passing through a mask, a line becoming a boundary, a camera following an action, or a deliberate cut. Design outgoing and incoming states together. Keep the new background behind the old one until coverage is complete. A dissolve between two dense text layouts usually produces unreadable overlap; stagger their exits and entrances or carry one object across.

## Animate relationships, not entire slide canvases

- Draw a connector as information moves along it; reveal a chart as its comparison is explained; unfold a real interface to direct attention to an action. Design at the object, line, letter, and layer level.
- Use masks, path drawing/morphing, carefully timed letter reveals, parallax, and frame-controlled 3D when they express the concept. Avoid applying every technique to every scene. Vary composition, scale, density, and rhythm across the film while retaining the visual system.
- Give movement acceleration, travel, and a settled state. Smooth cubic/quintic easing suits quiet editorial design; a critically damped spring can add weight without uncontrolled bounce. Keep camera movement restrained, especially around real interface text.
- Allow necessary text to be read after it settles. Rough starting points are about 0.3 seconds per word and roughly a second for a short label, adjusted for audience, narration, complexity, and viewing size. Do not use perpetual movement as a substitute for a clear hold.
- Reflow for portrait and square destinations. Check the full measured text width, safe areas, diagram labels, and footage focal points. Cropping a landscape film is often insufficient.

## Build a seekable local composition

Keep all source media and dependencies in the video project. Any LLM that can write files and invoke local tools can author this route. It does not require a particular model, a provider subscription, Skillry Premium, FavStash, or a cloud render account.

For the included renderer, expose this minimal contract from the HTML:

```js
window.MOTION_META = {
  width: 1920, height: 1080, fps: 30, duration: 12,
  reviewTimes: [0, 2.4, 2.7, 2.9666666667, 3, 3.0333333333, 4.5],
  events: [{ frame: 90, action: 'Visible connection completes', sound: 'soft click' }]
};
window.motionReady = document.fonts.ready;
window.renderFrame = async (seconds, viewport) => {
  // Derive and apply every visible state from seconds. Await media seeks here.
};
```

Frame numbers are the timing authority. Record a cue at the first frame where its intended event is visible, not automatically at the beginning of a fade. If fps changes, recheck that actual first-visible frame. Music and speech may determine the beat timing; sound is not mandatory for every object movement.

Make `renderFrame(t)` independent of prior calls. Pause any animation-library timelines and explicitly seek them. Avoid live clocks, running CSS animations, interactive-only state, and unseeded randomness. Wait for local images, fonts, and video seeks before returning. For an intentionally transparent composition, supply a proper alpha-capable render workflow; the bundled MP4 renderer exports opaque H.264.

The original [editable study](../assets/motion-starter/index.html) demonstrates a persistent contour, sampled shape morphing, line-level masked type, staged path drawing, layered vector illustration, and separate portrait layout. It uses built-in Canvas APIs, system fonts, and no external assets. It is a technique example: create a new composition and art direction for the actual subject rather than changing its headings for every video.

## Render with the included independent host

Install the free browser dependency once **in the video project**, retaining its lockfile and applicable notices:

```sh
npm install --save-exact playwright
npx playwright install chromium
```

Supply an installed FFmpeg binary with H.264 support. The repository's free Python runtime also exposes its bundled FFmpeg path through `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`. Run the Node script from any directory, using the actual installed script and composition paths:

```sh
node /path/to/creating-videos/scripts/render_motion.cjs /path/to/project/index.html --output /path/to/project/pilot.mp4 --ffmpeg /path/to/ffmpeg --stills-only
node /path/to/creating-videos/scripts/render_motion.cjs /path/to/project/index.html --output /path/to/project/pilot.mp4 --ffmpeg /path/to/ffmpeg
```

On Windows use quoted drive paths. `--width 1080 --height 1920` checks the composition's portrait treatment. An optional `--config design.json` sets `window.MOTION_CONFIG` before the page loads; the included study accepts palette, label, and four pairs of headline lines. Custom compositions choose their own configuration. `--duration` can shorten a pilot but cannot extend beyond the authored timeline. Use another filename for revisions; `--overwrite` explicitly permits replacing an existing MP4.

The host serves only local project files, blocks remote asset requests, captures deterministic frames, streams them to FFmpeg, saves review snapshots, and checks that reverse seeking reproduces the same pixels. It rejects running CSS/WAAPI animation, missing assets, page errors, invalid timing, and failed encoding. Snapshot times must include representative scene states and handoff boundaries; the example metadata shows how. It records technical results and leaves creative review pending.

This is a local HTML composition host, not a general website recorder or HyperFrames adapter. Use the separate HyperFrames CLI for a HyperFrames project; do not assume its runtime contract matches `renderFrame`. For complex real-time 3D, benchmark a short render and simplify shaders if necessary. Keep code and input media trusted and local.

## Finish and assess the actual film

Render a representative passage containing a complete handoff. Inspect scene states and start/middle/end transition frames at delivery size. Look for clipped text, accidental double images, unreadable labels, visual discontinuities, empty frames, misplaced elements, and unexplained decorative action. Review the continuous clip at normal speed before scaling the treatment.

The host exports silent visuals. Finish voice, music, ambience, effects, and captions with [the editing workflow](../../editing-videos/SKILL.md) and [local audio mixing](../../editing-videos/references/local-rendering.md). Keep cue times on the same frame grid, duck music under speech, and audition the full mix. Never call a silent render a completed narrated film. Do not substitute a primitive generated tone for a suitable musical arrangement merely to fill silence.

After revisions, review the final encoded video with sound. Keep the source composition, local assets, plan, sound cues, credits, captions, and review notes. A code check, deterministic seek, or successful encode establishes technical reliability, not whether the film is compelling.

## Research and attribution

Reviewed 2026-10-16. The linked Notion article points to a showreel prompt, a product-launch skill, and a creator editing pack. The public Skillry gallery illustrates many approaches and includes premium offerings; access to its gallery does not grant reuse rights to showcased films or audio. This guide and its implementation are independently written. No third-party skill text, artwork, footage, music, or code has been copied into the starter.

- [Notion resource guide](https://sketricsolutions.notion.site/Make-Claude-your-motion-designer-the-3-resources-behind-every-Opus-5-5-video-3eade0351eaa81319d74dfaad5e89a70): starting from a concrete visual brief and inspecting scenes before rendering.
- [Skillry public gallery](https://skillry.dev/ai-videos/opus-5-5): examples of coordinated typography, shape transitions, browser-based artwork, and 3D. Creator prompts and model attributions are claims on the page, not a quality benchmark reproduced by this repository.
- [brag / brag-slim](https://github.com/latent-spaces/brag): MIT code; useful practices include inspecting the real product, designing a specific short story, using readable copy, and reviewing intermediate frames.
- [FavStash creator skills](https://github.com/alisadiq-ai/favstash-ai-video-editing-skills): Apache-2.0 original materials with separate third-party notices; useful practices include object continuity, frame-aligned sound events, safe-area review, and inspecting the encoded export. This workflow does not install its connector, publish anything, or depend on its service.
- [Playwright screenshot API](https://playwright.dev/docs/api/class-page#page-screenshot) and [FFmpeg documentation](https://ffmpeg.org/ffmpeg.html): underlying local capture and encoding tools; retain their applicable dependency notices.
