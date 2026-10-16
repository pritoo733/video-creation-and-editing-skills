# Local Video Production Dashboard

## Purpose

Give creators a private, quick overview of video projects made with this repository. The dashboard reads existing output folders on the creator's computer; it does not require a hosted account or upload project information.

## User and success criteria

The primary user is a creator who wants to see how many videos have been produced, which productions are complete or still in progress, and what production milestones and assets each project has. A successful first run makes the chosen output library understandable without editing JSON by hand.

## Proposed approach

Add a small local-only Python HTTP server and a static web interface. The user starts it with a path to a folder containing video project output folders. The server scans that folder read-only, serves a JSON summary, and serves preview videos only from discovered project directories. The UI has a refresh action; it does not persist analytics or modify project data.

No new Python package is required. The server binds to `127.0.0.1` by default and rejects paths outside the configured library root. The library root is selected when starting the server, not through arbitrary browser file access.

## Dashboard content

- Summary cards: completed videos, projects in progress, total project count, and total rendered runtime.
- A searchable, sortable project list with title, status, updated/created timestamp when available, duration, resolution/orientation, narration provider/voice when recorded, shot count, and footage-versus-graphics counts when available.
- Production milestones derived only from recorded artifacts/logs: plan/shot list, storyboard, narration/audio, captions, final render, and creative review. Unknown values remain “Not recorded”; a report only marks creative review complete when it records an explicit pass/approval.
- Per-project details with a local video preview when `final.mp4` exists, links to storyboard, credits, captions, and review report when present, plus recorded source/license information.
- An honest empty state with instructions to start the server against the folder where generated outputs are saved.

## Discovery and status rules

- A project is discovered from `plan.json`, `production-log.json`, `timeline.json`, or a top-level deliverable MP4 beneath the chosen root. Review files enrich a discovered project but do not create a project on their own, which keeps isolated review-only folders out of the library.
- A rendered video is counted as completed when a non-empty top-level MP4 deliverable exists in the project folder. This includes canonical `final.mp4` and named final exports; obvious `visuals*`, `pilot*`, `*-pilot*`, `original-vs-revised`, and working-folder renders are excluded. Each deliverable is counted as a video, so one project may contain multiple versions. A plan or run log without a deliverable is in progress; a log status of failed is shown as failed.
- Runtime and dimensions come from existing review/timeline metadata when reliable; if unavailable, the dashboard reports them as unavailable rather than probing with a new dependency.
- Milestone state is taken from existing artifact files and production-log status entries. This dashboard does not score creative quality, infer ad results, count views, or claim progress that was not recorded.
- Only recognized output names and metadata are displayed; working intermediates are excluded from completed-video counts.

## Security and privacy

- Localhost-only by default; no authentication because the server is not exposed to the network.
- All resolved file paths must remain under the configured root. The browser cannot submit an arbitrary path for the server to open.
- Read-only project access: no delete, rename, render, or edit actions.
- Escape metadata before rendering it into HTML. Do not transmit local metadata to external services.

## Visual direction

An operational creator dashboard: dark ink/navy canvas, warm off-white panels, restrained teal accent, compact but readable status chips, clear hierarchy, and a real playable video preview in the project detail. Responsive layout should remain useful on laptop and mobile widths. Avoid fake charts, vanity scores, and decorative metrics without source data.

## Scope exclusions

- No cloud hosting, account system, remote sync, analytics collection, generation controls, or paid services.
- No automatic video quality score, social performance tracking, or view/engagement metrics.
- No edits to existing video output folders or production manifests.

## Acceptance criteria

1. Starting the documented command opens a dashboard in a browser and scans only the supplied library root.
2. Summary counts distinguish completed videos from incomplete and failed projects using the rules above.
3. Project search/filter and details work for both full and partial metadata.
4. Existing `final.mp4` output plays in the dashboard; artifact links resolve only within the selected root.
5. Missing or malformed metadata produces a useful partial record instead of crashing the dashboard.
6. The interface has a clear empty state, refresh action, keyboard-accessible controls, and responsive layout.
7. No project metadata leaves localhost, and attempts to request paths outside the configured root are rejected.

## Open interpretation

The phrase “used for level-ups” is interpreted as progress through recorded production milestones, not creator gamification or an automatically calculated quality level.
