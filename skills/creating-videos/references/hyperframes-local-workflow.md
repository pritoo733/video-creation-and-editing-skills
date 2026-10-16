# HyperFrames local workflow

Use [HyperFrames](https://github.com/heygen-com/hyperframes) when a project needs polished, editable motion graphics, kinetic typography, animated diagrams/charts, reusable titles, captions, overlays, or mixed HTML-and-media scenes. Its source repository is Apache-2.0 and describes local preview and MP4 rendering without per-render fees or commercial-use thresholds. The command-line path requires Node.js 22+ and FFmpeg. Recheck current upstream requirements and license before installing.

HyperFrames is an optional route for any LLM with shell access and Node.js support. It is not a hosted video-generation service. Keep the workflow local: do not use hosted cloud render, the HyperFrames web playground, HeyGen APIs, AWS Lambda, or paid media providers in a free-only project. The renderer may download its npm packages/browser components during setup; this is an install-time network requirement, not a paid generation call.

## Where it improves this repository

- **More expressive animation:** Author scenes as normal HTML/CSS, SVG/canvas, and seekable GSAP or other supported animation. This is a better fit than a slide-like renderer for kinetic type, animated data, interface callouts, layered product visuals, and branded motion systems.
- **Frame-accurate and repeatable output:** The renderer seeks exact timeline frames in headless Chrome, then encodes with FFmpeg. Make animation a function of the requested composition time; avoid wall-clock timers, unseeded randomness, live network requests, or state that depends on which frames were rendered before it.
- **Inspectable production stages:** Use init → lint → preview → check/snapshot → render. Read warnings and inspect the preview at normal playback speed before encoding the full piece. A successful `render` alone does not prove the design, story, or motion is good.
- **Video-first design system:** Create a project `frame.md` from approved brand fonts/colors/tokens, then derive compositions from those values. Keep brand details exact and distinguish real logos/product UI from invented illustrative graphics.
- **Reusable parts:** Save original transitions, lower thirds, charts, and scene components in the project. Search the HyperFrames catalog for a story-specific starting point, then check the exact block and every bundled dependency before use. The framework license does not automatically cover third-party media, fonts, models, or catalog assets.
- **Agent portability:** Keep the main video project as editable HTML, local assets, a short `STORYBOARD.md`, `SCRIPT.md` when narrated, and project metadata. The file-based handoff works across LLMs; no specific model provider is required.

## Start a local project

First confirm the machine has Node.js 22 or later, FFmpeg on PATH, enough disk for npm/browser packages and source assets, and permission to install dependencies. From a separate video project folder:

```sh
npx hyperframes init my-video
cd my-video
npx hyperframes preview
npx hyperframes lint
npx hyperframes check
npx hyperframes render
```

Use the current upstream CLI help if any command differs. Do not put generated media or `node_modules` in this skills repository. Keep the resulting project self-contained, with local media under `assets/` and renders outside source directories.

## Find and use catalog blocks

The [HyperFrames catalog](https://hyperframes.heygen.com/catalog) provides reusable blocks and components. They can add a polished visual motif quickly, but treat them as editable ingredients rather than a whole-video template. Search by the actual story beat and action (for example, “a timeline that reveals steps one by one” or “a restrained 3D product title”), not by vague requests such as “make it cinematic.”

From the video project folder, browse or search, then install only the selected item:

```sh
npx hyperframes catalog --json
npx hyperframes catalog --type block --tag transition
npx hyperframes catalog --query "a clean animated data comparison"
npx hyperframes add <selected-item-name>
```

Use `npx hyperframes catalog --help` if the installed CLI has different options. `catalog --json` provides catalog details such as name, type, description, tags, dimensions, duration, and preview URLs; it does not establish that the item and all its dependencies are cleared for the intended use. The CLI docs recommend explicit `add` after browsing in automated workflows.

Before installing or distributing a block, complete the [catalog block review](../../../templates/hyperframes-catalog-review.md): inspect its source and license, then inspect imported, vendored, or remotely loaded packages, media, fonts, logos, and attribution notices. Record each source and its exact license. Keep only items whose terms allow the planned personal or commercial use at zero cost. If a dependency's terms are unclear, require a paid tier, or prohibit the intended use, skip that item and choose another or create an original local component. Do not treat a preview or catalog listing as a rights grant.

After rights review, adapt the block to the scene's message, colors, type, timing, and accessibility needs. Check that it works offline during render: replace remote runtime/media dependencies with cleared local copies when their licenses permit, or choose another block. Run lint and browser checks, preview at normal speed, and render a short representative passage before using the treatment throughout a video. Avoid repeating a signature block across adjacent scenes; each installation should serve a specific story beat.

The upstream repository currently describes seven contributed 3D catalog pieces as being under its Apache-2.0 license, while also calling out bundled or remotely loaded dependencies with separate terms, including GSAP under its Standard License. That is a useful example of why the block and dependency review must be separate; it is not a blanket license statement for the changing catalog. Recheck current source notices at selection time.

## Production sequence

1. **Storyboard before layout.** State the audience, story, duration, aspect ratio, visual thesis, and final viewer action. For every scene record narration, on-screen action, source/assets, timing, and why the visual belongs to that beat. Do not turn every sentence into a separate title card.
2. **Set visual rules.** Write project `frame.md` with frame size, colors, typography, safe margins, spacing, text hierarchy, image treatments, and a small set of motion principles. Preserve approved brand tokens; do not invent a logo or fabricate a product state.
3. **Plan a varied sequence.** Mix genuine footage/screen captures with motion graphics when each adds evidence or clarity. Use distinct visual sources and shot scales; support abstract claims with original diagrams rather than unrelated stock. Allow enough hold time for UI, charts, and disclosures to be read.
4. **Author seekable scenes.** Keep media local and verify every path, font, image, and audio file is available during render. Use timeline-driven animations that seek to the same visual state at any time value. Follow HyperFrames' composition/timeline rules and do not separately control framework-owned media playback.
5. **Run the review gates.** Lint the composition; preview the sequence; run the browser check; snapshot representative times and every scene boundary; inspect the opening, transitions, and ending. Review at target size and normal speed. Fix missing media, browser errors, clipping, color contrast, unintended overlap, inconsistent type, and frame-seek differences before final render.
6. **Finish audio and captions.** Keep the final voice/music/effects mix and captions tied to the real final edit. Ensure music does not mask speech. After timing changes, regenerate or retime captions and preview them on actual footage.
7. **Render and verify.** Render locally, check the MP4 with FFprobe/decoder, then watch the final result with sound. Save the composition source, storyboard, local media/source and license ledger, settings, and review notes beside the export.

## Use HyperFrames with the existing workflows

Choose HyperFrames for a graphics-led video or a hybrid composition that benefits from editable HTML animation. Choose the existing [shot composer](../../editing-videos/references/shot-composition.md) when its manifest flow fits a sequence of real video intervals, camera footage, screen recordings, and paced UI scrolling. A hybrid project can use HyperFrames for titles and transitions and the local footage workflow for source inspection and media preparation. Keep one timeline as the timing authority; avoid separately retiming duplicate versions of the same scene.

HyperFrames can make motion precise and repeatable, but it cannot decide what story should be told or make generic graphics feel authentic. Use original composition, real action, relevant imagery, restrained typography, purposeful sound, and a full human review to avoid a template-heavy result.

## License and cost boundary

The framework repo is Apache-2.0, and its README describes the local CLI path as having no per-render fee. That does not license input footage, music, fonts, logos, generated media, or separately installed registry components. Keep the composition local and use only assets whose exact license and attribution are recorded. Cloud render, AWS Lambda, external APIs, and hosted design/playground features are outside this free-local route. “Free to install” and “free to use in this video” are separate checks.
