(() => {
  const byId = (id) => document.getElementById(id);
  const state = { projects: [], selected: null, scannedAt: null };
  const labels = { complete: 'Rendered', in_progress: 'In production', failed: 'Needs attention', unknown: 'Partial data' };
  const artifactLabels = [
    ['storyboard.html', 'Storyboard'], ['CREDITS.md', 'Credits'], ['captions.srt', 'Captions'],
    ['captions.ass', 'Styled captions'], ['transcript.json', 'Transcript'], ['shots.json', 'Shot list'],
    ['timeline.json', 'Timeline'], ['asset-ledger.json', 'Asset ledger'],
    ['google-flow-assets.json', 'Google Flow assets'],
    ['review.json', 'Review report'], ['review-contact-sheet.jpg', 'Contact sheet'],
  ];

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function prettyDuration(seconds) {
    if (seconds === null || !Number.isFinite(Number(seconds))) return '—';
    const total = Math.max(0, Math.round(Number(seconds)));
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const secs = total % 60;
    return hours ? `${hours}h ${minutes}m` : minutes ? `${minutes}m ${secs}s` : `${secs}s`;
  }

  function displayDate(value) {
    if (!value) return 'Date unavailable';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? 'Date unavailable' : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(date);
  }

  function projectStatus(project) {
    return labels[project.status] || labels.unknown;
  }

  function summary() {
    const ready = state.projects.reduce((total, project) => total + (Number(project.video_count) || 0), 0);
    const progress = state.projects.filter((project) => project.status === 'in_progress');
    const failed = state.projects.filter((project) => project.status === 'failed');
    const duration = state.projects.reduce((total, project) => total + (Array.isArray(project.videos)
      ? project.videos.reduce((sum, video) => sum + (Number(video.duration) || 0), 0)
      : Number(project.duration) || 0), 0);
    byId('metric-complete').textContent = String(ready);
    byId('metric-progress').textContent = String(progress.length);
    byId('metric-failed').textContent = String(failed.length);
    byId('metric-runtime').textContent = duration ? prettyDuration(duration) : '—';
    byId('project-count').textContent = String(state.projects.length);
    byId('scan-status').textContent = state.scannedAt ? `Updated ${new Intl.DateTimeFormat(undefined, { timeStyle: 'short' }).format(new Date(state.scannedAt))}` : 'Local library';
  }

  function visibleProjects() {
    const query = byId('search').value.trim().toLocaleLowerCase();
    const status = byId('status-filter').value;
    return state.projects.filter((project) => {
      const searchText = [project.title, project.brief, project.path, project.status].join(' ').toLocaleLowerCase();
      return (!query || searchText.includes(query)) && (status === 'all' || project.status === status);
    });
  }

  function renderList() {
    const list = byId('project-list');
    list.replaceChildren();
    const projects = visibleProjects();
    byId('no-results').hidden = state.projects.length === 0 || projects.length > 0;
    for (const project of projects) {
      const button = el('button', 'project-row');
      button.type = 'button';
      button.setAttribute('role', 'listitem');
      button.setAttribute('aria-current', String(project.id === state.selected));
      button.setAttribute('aria-label', `${project.title}, ${projectStatus(project)}`);
      const main = el('span', 'project-copy');
      const titleline = el('span', 'project-main');
      titleline.append(el('span', 'project-name', project.title));
      const pathline = el('span', 'project-path', project.path || 'Project folder');
      main.append(titleline, pathline);
      const side = el('span', 'project-side');
      const badge = el('span', `status ${project.status || 'unknown'}`, projectStatus(project));
      const format = project.width && project.height ? `${project.width} × ${project.height}` : 'Format unavailable';
      const videoCount = Number(project.video_count) || 0;
      const projectInfo = videoCount ? `${videoCount} ${videoCount === 1 ? 'video' : 'videos'}${project.duration !== null ? ` · ${prettyDuration(project.duration)}` : ''}` : format;
      side.append(badge, el('span', 'project-format', projectInfo));
      button.append(main, side);
      button.addEventListener('click', () => {
        state.selected = project.id;
        renderList();
        renderDetail(project);
      });
      list.append(button);
    }
  }

  function addLink(parent, project, file, label) {
    if (!project.artifacts || !project.artifacts[file]) return;
    const link = el('a', 'artifact-link', label);
    link.href = `/media/${encodeURIComponent(project.id)}/${encodeURIComponent(file)}`;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    parent.append(link);
  }

  function renderDetail(project) {
    const panel = byId('project-detail');
    panel.replaceChildren();
    const head = el('header', 'detail-head');
    const top = el('div', 'detail-topline');
    top.append(el('h2', 'detail-title', project.title), el('span', `status ${project.status || 'unknown'}`, projectStatus(project)));
    head.append(top);
    if (project.brief) head.append(el('p', 'detail-brief', project.brief));
    const facts = el('div', 'detail-stats');
    facts.append(el('span', '', displayDate(project.updated_at)));
    if (project.duration !== null) facts.append(el('span', '', prettyDuration(project.duration)));
    if (project.width && project.height) facts.append(el('span', '', `${project.width} × ${project.height}${project.fps ? ` · ${project.fps} fps` : ''}`));
    if (project.shot_count !== null && project.shot_count !== undefined) facts.append(el('span', '', `${project.shot_count} planned shots`));
    if (project.stock_count !== null && project.graphic_count !== null) facts.append(el('span', '', `${project.stock_count} footage · ${project.graphic_count} graphics`));
    if (project.flow_count) facts.append(el('span', '', `${project.flow_count} Google Flow clips`));
    if (project.voice && project.voice.provider) facts.append(el('span', '', `${project.voice.provider}${project.voice.voice ? ` · ${project.voice.voice}` : ''}`));
    head.append(facts);
    panel.append(head);

    const frame = el('div', 'video-frame');
    if (project.has_video) {
      const videos = Array.isArray(project.videos) ? project.videos : [];
      let selectedVideo = videos.find((video) => video.name === project.primary_video) || videos[0];
      if (videos.length > 1) {
        const selectorWrap = el('label', 'video-selector');
        selectorWrap.append(el('span', '', 'Preview cut'));
        const selector = document.createElement('select');
        selector.setAttribute('aria-label', 'Choose a video to preview');
        for (const videoInfo of videos) {
          const option = document.createElement('option');
          option.value = videoInfo.name;
          option.textContent = `${videoInfo.title}${videoInfo.duration !== null ? ` · ${prettyDuration(videoInfo.duration)}` : ''}`;
          selector.append(option);
        }
        selector.value = selectedVideo.name;
        selectorWrap.append(selector);
        frame.append(selectorWrap);
      }
      const video = document.createElement('video');
      video.controls = true;
      video.playsInline = true;
      video.preload = 'metadata';
      video.setAttribute('aria-label', `Preview of ${project.title}`);
      video.src = `/media/${encodeURIComponent(project.id)}/${encodeURIComponent(selectedVideo.name)}`;
      const selector = frame.querySelector('select');
      if (selector) selector.addEventListener('change', () => {
        video.pause();
        video.src = `/media/${encodeURIComponent(project.id)}/${encodeURIComponent(selector.value)}`;
        video.load();
      });
      frame.append(video);
    } else {
      const unavailable = el('div', 'video-unavailable');
      unavailable.append(el('p', '', project.status === 'failed' ? 'This production stopped before a final video was created.' : 'Final video has not been rendered yet.'));
      frame.append(unavailable);
    }
    panel.append(frame);

    const content = el('div', 'detail-content');
    content.append(el('h3', 'milestone-heading', 'Production milestones'));
    const list = el('ul', 'milestones');
    for (const milestone of project.milestones || []) {
      const item = el('li', `milestone ${milestone.state || 'unknown'}`);
      const glyph = milestone.state === 'complete' ? '✓' : milestone.state === 'unknown' ? '·' : '–';
      item.append(el('span', 'milestone-dot', glyph), el('span', '', `${milestone.name}${milestone.state === 'unknown' ? ' · not recorded' : ''}`));
      list.append(item);
    }
    content.append(list);

    const links = el('nav', 'artifact-links');
    links.setAttribute('aria-label', 'Project files');
    for (const [file, label] of artifactLabels) addLink(links, project, file, label);
    for (const storyboard of project.storyboards || []) {
      if (['storyboard.html', 'storyboard.json'].includes(storyboard)) continue;
      addLink(links, { ...project, artifacts: { ...(project.artifacts || {}), [storyboard]: true } }, storyboard, 'Storyboard');
    }
    for (const report of project.reports || []) {
      if (report === 'review.json') continue;
      addLink(links, { ...project, artifacts: { ...(project.artifacts || {}), [report]: true } }, report,
        report.replace(/\.json$/i, '').replace(/[-_]+/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()));
    }
    if (links.childElementCount) content.append(links);

    if (project.sources && project.sources.length) {
      content.append(el('h3', 'source-heading', 'Recorded source & license notes'));
      const sources = el('ul', 'source-list');
      for (const source of project.sources) {
        const row = el('li');
        const url = safeExternalUrl(source.url);
        if (url) {
          const anchor = el('a', '', source.title);
          anchor.href = url;
          anchor.target = '_blank';
          anchor.rel = 'noopener noreferrer';
          row.append(anchor);
        } else row.append(el('span', '', source.title));
        const licenseUrl = safeExternalUrl(source.license_url);
        if (licenseUrl) {
          const license = el('a', 'source-license', source.license);
          license.href = licenseUrl;
          license.target = '_blank';
          license.rel = 'noopener noreferrer';
          row.append(license);
        } else row.append(el('span', 'source-license', source.license));
        sources.append(row);
      }
      content.append(sources);
    }
    if (project.latest_error) content.append(el('p', 'error-detail', project.latest_error));
    panel.append(content);
  }

  function safeExternalUrl(value) {
    try {
      const url = new URL(value);
      return ['https:', 'http:'].includes(url.protocol) ? url.href : null;
    } catch { return null; }
  }

  async function loadProjects() {
    const refresh = byId('refresh');
    refresh.disabled = true;
    refresh.classList.add('is-refreshing');
    byId('error-banner').hidden = true;
    try {
      const response = await fetch('/api/projects', { cache: 'no-store' });
      if (!response.ok) throw new Error(`Library scan failed (${response.status}).`);
      const payload = await response.json();
      state.projects = Array.isArray(payload.projects) ? payload.projects : [];
      state.scannedAt = payload.scanned_at || null;
      if (!state.projects.some((project) => project.id === state.selected)) state.selected = state.projects[0]?.id || null;
      summary();
      byId('empty-state').hidden = state.projects.length > 0;
      byId('workspace').hidden = state.projects.length === 0;
      renderList();
      const selected = state.projects.find((project) => project.id === state.selected);
      if (selected) renderDetail(selected);
    } catch (error) {
      byId('error-banner').textContent = `${error.message} Check that the local dashboard server is running, then refresh.`;
      byId('error-banner').hidden = false;
      byId('scan-status').textContent = 'Library scan unavailable';
    } finally {
      refresh.disabled = false;
      refresh.classList.remove('is-refreshing');
    }
  }

  byId('refresh').addEventListener('click', loadProjects);
  byId('search').addEventListener('input', renderList);
  byId('status-filter').addEventListener('change', renderList);
  loadProjects();
})();
