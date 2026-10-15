# Select tools for the production need

Check installed capabilities, hardware, rights, costs, and export access before choosing the route. These are options, not dependencies of the skill. Source links were checked on 2026-10-15; current versions and terms can change.

| Need | Suitable route | Practical boundary |
| --- | --- | --- |
| Reproducible footage assembly, trim, crop, transitions, overlays, captions, audio | [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html), with the editing skill's `scripts/compose_video.py` | Works locally with Python standard library plus FFmpeg. Requires actual media; does not source footage or create cinematic images by itself. |
| Custom Python composition | [MoviePy](https://zulko.github.io/moviepy/) | Useful for compositing and effects; inspect installed API/version and benchmark a pilot. It does not choose good shots for the editor. |
| React-based motion design, diagrams, precise typography | [Remotion](https://www.remotion.dev/docs/) | Use when authored graphics serve the story. Check [current licensing](https://www.remotion.dev/docs/license/pricing): eligibility for free commercial use depends on the organization; do not assume all use is free. |
| Advanced color, tracking, compositing, audio finishing, editable timelines | [DaVinci Resolve/Fusion/Fairlight](https://www.blackmagicdesign.com/products/davinciresolve) | Verify the installed edition, automation interface, hardware, and available features. Free and Studio capabilities differ. |
| Original 3D scenes or camera animation | [Blender](https://www.blender.org/features/) | Use for a genuine 3D need; allow time for scene design and rendering. An animated diagram may be more useful and cheaper to produce. |

For a footage-led promo, use a timeline that accepts real video intervals rather than a renderer whose primary abstraction is one image/text layout per paragraph. Normalize frame rate, time base, dimensions, rotation, and pixel format before transitions. Account for overlap in the final runtime. Rebuild captions from final speech timing after edits. Keep source audio/dialogue sync when relevant; the included composer uses a supplied final mix and does not perform dialogue editing or J/L cuts automatically.

Use the editing skill's [composition guide](../../editing-videos/references/shot-composition.md) for the bundled manifest renderer. Its cache/logs support revisions and its timing checks catch truncated sources; editorial decisions, licensing review, and audiovisual review remain part of the workflow.
