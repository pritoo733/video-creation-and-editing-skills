# Local Video Production Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private local web dashboard that summarizes generated video projects and their recorded production milestones.

**Architecture:** A dependency-free Python `ThreadingHTTPServer` scans a user-supplied project library read-only and exposes a small JSON API. A static responsive dashboard renders summaries, filters, milestone details, and safe local video/artifact links; the server only serves files discovered beneath the configured root.

**Tech Stack:** Python standard library, semantic HTML, CSS, and vanilla JavaScript.

**Spec:** [2026-10-16-local-video-dashboard-design.md](../specs/2026-10-16-local-video-dashboard-design.md)

## Global Constraints

- Bind to `127.0.0.1` by default; no cloud service or analytics.
- Add no Python or JavaScript dependencies.
- Read project folders without modifying them.
- Reject paths outside the configured library root and escape metadata in the UI.
- Count each non-empty top-level MP4 deliverable, including named final exports, while excluding obvious `visuals`, `pilot`, comparison, and working renders.
- Represent missing metadata as unavailable; never infer quality or performance.
- Do not add or run an automated test suite unless the user asks; perform syntax and visual preview checks for the requested dashboard.

## Review Focus

- Malformed or missing JSON must not take down the dashboard; show partial project details.
- Symlinks, URL-encoded paths, or crafted artifact IDs must not expose files outside the selected root.
- Nested working folders and intermediate MP4s must not inflate completed-video counts.
- Long titles and empty libraries must remain readable at desktop and mobile widths.
- Unknown production metadata must not be represented as completed milestones.

## File Map

- `scripts/video_dashboard.py` — CLI, recursive scanner, safe JSON normalization, localhost API, and safe artifact serving.
- `dashboard/index.html` — semantic page structure and accessible controls.
- `dashboard/dashboard.css` — responsive operational dashboard visual system.
- `dashboard/dashboard.js` — fetch, summary cards, filtering, project list, and detail rendering.
- `README.md` — quick start, output-folder selection, privacy behavior, and dashboard features.
- `skills/creating-videos/references/automatic-free-production.md` — link the dashboard from the automatic production workflow.

### Task 1: Add the read-only local scanner and server

**Files:**
- Create: `scripts/video_dashboard.py`

**Interfaces:**
- CLI: `python scripts/video_dashboard.py --root <folder> [--host 127.0.0.1] [--port 8765] [--open]`.
- `scan_library(root: Path) -> list[dict]` returns normalized projects with stable IDs, output-relative artifact names, parsed status, milestones, and optional media metadata.
- `GET /api/projects` returns `{projects: [...], scanned_at: ISO8601}`.
- `GET /media/<project-id>/<artifact>` serves only whitelisted artifacts belonging to a discovered project and contained in root.

- [ ] Implement recursive project discovery from known markers; skip VCS, virtualenv, dependency, and working/intermediate directories.
- [ ] Normalize `plan.json`, `production-log.json`, `review.json`, `timeline.json`, `audio-tracks.json`, `storyboard.json`, `CREDITS.md`, and `final.mp4` defensively.
- [ ] Derive status and milestone values using the spec; provide unavailable values for absent data.
- [ ] Implement localhost server routes and strict resolved-path containment for media/artifact requests.
- [ ] Add CLI help, root validation, browser opening, and useful startup messages.
- [ ] Run Python syntax compilation and manually inspect scanner/server behavior against the existing automatic-free example plus a partial project directory; do not add/run automated tests.

### Task 2: Build the creator dashboard page

**Files:**
- Create: `dashboard/index.html`
- Create: `dashboard/dashboard.css`
- Create: `dashboard/dashboard.js`

**Interfaces:**
- Page loads `/api/projects` and renders project fields from the normalized schema in Task 1.
- Controls: search input, status filter, refresh button, project detail disclosure, and local video preview.

- [ ] Create a responsive page with four real summary metrics, a compact project table/list, a useful empty state, and clear loading/error states.
- [ ] Implement searchable/sortable projects and status filters without new libraries.
- [ ] Show recorded milestones, voice provider/voice, format, duration, footage/graphics counts, and links only when data exists.
- [ ] Render video preview and storyboard/credits/caption/review links through safe server routes.
- [ ] Escape untrusted text, preserve keyboard accessibility, and use no external fonts, scripts, analytics, or assets.
- [ ] Open a local preview at desktop and mobile sizes, inspect actual page renders, and make one consolidated visual correction pass.

### Task 3: Document and hand off the dashboard

**Files:**
- Modify: `README.md`
- Modify: `skills/creating-videos/references/automatic-free-production.md`

- [ ] Document the Windows and macOS/Linux launch commands, how to select the folder containing outputs, and that the server is local and read-only.
- [ ] Explain that “milestones” reflect recorded artifacts and that ad views/performance are not tracked.
- [ ] Run `python -m py_compile scripts/video_dashboard.py` and `git diff --check`; open the dashboard preview for the user.

## Execution notes

Implement directly in this session. Do not expose the server to LAN by default. Do not push the change until the completed page has been shown to the user and the repository diff reviewed.
