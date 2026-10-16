# Motion library for video graphics

Use [Motion](https://github.com/motiondivision/motion) when a scene needs refined HTML, SVG, or React animation: kinetic type, animated diagrams, callouts, UI highlights, data reveals, and reusable branded transitions. Motion is an animation library, not a video editor or encoder. The repository's automatic Python renderer does **not** currently import Motion; it renders a small set of Pillow process and bar-chart graphics. This guide adds Motion as an optional authoring route for richer scenes.

## What is free

The open-source [`motion`](https://www.npmjs.com/package/motion) package is MIT-licensed. Install it in the video project's own Node workspace, pin the resolved version in its lockfile, and keep its license notice with the handoff. Motion+ contains paid examples, components, and tools; this workflow uses only the open-source package and public documentation. Check the current upstream license before distribution.

```sh
npm install --save-exact motion
```

## Pick the right route

| Need | Route |
| --- | --- |
| Simple process reveal or sourced bar chart in an automatic-free project | Existing local Python renderer (`motion_graphics.py`) |
| Rich HTML/SVG/React motion, typography, data, or interface callouts | Motion library for scene animation, paired with a deterministic local capture/render host |
| Full video timeline, scene composition, preview, and local MP4 rendering | [HyperFrames workflow](hyperframes-local-workflow.md), with Motion only where its composition runtime can reliably seek the scene |
| Textured, hand-drawn art direction | [p5.js and p5.brush guide](motion-graphics.md) |

Use Motion for scenes whose information benefits from precise animated state changes. Keep footage and real screen recordings as evidence; use graphics to explain relationships or direct attention, not as decorative filler.

## Build a renderable scene

1. Write the scene's purpose, narration line, visual action, duration, and final settled state in the storyboard. Design the animation to reveal one idea at a time, then leave a readable hold.
2. Author the scene in local HTML/SVG or React. Use Motion's `animate()` controls for explicit time-based transitions. Keep scene time as the only source of progress; avoid hover, scroll position, timers, uncontrolled random values, live data, and state that depends on the prior frame.
3. Expose a scene-level `seek(seconds)` function. It must pause and set every active Motion playback control to the requested scene time (Motion controls expose a writable `time` in seconds), apply any scene-level state, then wait for the browser to paint before capture. Clamp times to the scene duration. Keep control references and each animation's start offset so staggered elements seek consistently.
4. Connect `seek(seconds)` to a local frame renderer such as the HyperFrames timeline/capture path or another browser renderer that can request exact timestamps. Motion supplies animation; the host supplies frame scheduling, audio synchronization, and MP4 encoding. Do not assume ordinary browser playback or a screen recording is frame-accurate.
5. Before rendering a full video, render a representative scene. Request frames in a non-sequential order (for example, 1.2s, 0.3s, 1.2s); identical requested times must produce visually identical frames. Confirm that fonts and local assets are loaded before seeking.
6. Render the full scene locally, inspect a contact sheet and normal-speed playback, and repair clipping, missed paint frames, abrupt starts/ends, flicker, small text, or motion that does not support the narration. Keep the source scene, pinned dependencies, timing, local assets, and review notes together.

Motion documents that `animate()` returns playback controls and that their `time` can be read or set. Use this capability to make a scene seekable; it does not by itself guarantee deterministic rendering. Verify behavior in the actual selected capture engine, especially when using spring physics, React state, canvas, or JavaScript callbacks.

## Motion design rules for generated scenes

- Animate hierarchy and information: establish the subject, reveal supporting detail, resolve the movement, and hold long enough to understand it.
- Use a small set of scene-specific transitions. Match movement to the concept (for example, a path drawing for a route or nodes connecting for a workflow).
- Prefer opacity, transforms, SVG path drawing, masks, and restrained number changes. Keep data values, product UI, and source footage accurate.
- Keep titles and captions readable at the delivery size. Respect safe areas and don't animate essential copy faster than it can be read.
- Avoid defaulting every scene to the same spring, bounce, zoom, particle field, or text reveal. Reuse a visual system, not identical scene compositions.
- Review transition frames as well as scene keyframes. A polished opening and ending do not compensate for mismatched middle scenes.

## Review checklist

- [ ] `seek(t)` returns the same frame for the same time, including when frames are requested out of order.
- [ ] The capture host waits for fonts, images, video, and Motion updates before taking a frame.
- [ ] No browser console errors, missing assets, black frames, blank SVG/canvas, or dropped joins.
- [ ] Motion clarifies the narrated idea and leaves readable holds; effects don't obscure faces, evidence, or controls.
- [ ] The complete encoded video is reviewed at normal speed with audio, not just sampled stills.
- [ ] Project records list the Motion package version, license, render settings, media rights, and any review limitations.

## Official references

- [Motion source and MIT license](https://github.com/motiondivision/motion)
- [Motion `animate()` and playback controls](https://motion.dev/docs/animate)
- [Motion for React](https://motion.dev/docs/react)
