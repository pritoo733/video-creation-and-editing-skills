# Original motion graphics with p5.js and p5.brush

Use custom animation when it explains an idea, reveals a process, gives a product a distinctive visual language, or connects scenes. Movement alone does not make a video engaging. Every effect must have a stated story purpose and should not obscure evidence, captions, or UI.

## p5.js + p5.brush route

[p5.js](https://github.com/processing/p5.js) is a creative-coding library. [p5.brush](https://github.com/acamposuribe/p5.brush) adds pencil/charcoal/marker strokes, watercolor-like fills, hatching, and vector-field movement. The p5.brush project is MIT-licensed and currently requires p5.js 2.x with a WEBGL canvas, or its standalone WebGL2 build. p5.js is LGPL-2.1; preserve its license and attribution if bundling or modifying it. Check the current upstream licenses, browser support, and versions before production.

Use p5.brush selectively for original, story-specific artwork: a hand-drawn route, a textured transition revealing a concept, a technical process forming from strokes, or an organic mask over a sourced shot. Keep product interfaces and factual charts crisp. Avoid adding watercolor or brush marks to every scene; reserve the look for a coherent visual motif.

### Animation handoff

1. Write one sentence for the scene's purpose and identify the visual metaphor.
2. Create a self-contained sketch in the project's `graphics/` folder. Set a fixed canvas size, frame rate, deterministic random/noise seed, palette, typography, and background. Use scene time (not uncontrolled wall-clock randomness) so frames can be reproduced.
3. Design its entrance, hold/read period, and exit around the narration and edit. Animate the focal point, layered depth, stroke reveal, or camera; avoid a static drawing that only wiggles.
4. Render locally in a browser/capture tool available on the machine, or export numbered frames and encode them with FFmpeg. Do not depend on a hosted rendering or paid asset service. If a browser is used, wait for fonts/assets to load and verify the captured canvas is not blank.
5. Inspect a contact sheet and playback at normal speed. Check edges, flicker, text size, loop seams, dropped frames, color contrast, and consistency with neighboring shots. Include the sketch and render settings in the editable handoff.

Do not copy the p5.brush source into this repository. Add it as a project dependency only when the required p5 version and WebGL path are available; lock versions and retain upstream notices. If unavailable, make the same visual with local FFmpeg, SVG, Canvas, or another already-installed route and preserve the intended art direction.

## State-driven orb animation inspiration

[thinking-orbs](https://github.com/Jakubantalik/thinking-orbs) is an MIT-licensed library of distinct dotted 2D canvas animations for agent UI states (for example searching, solving, listening, and connecting). It is not a video editor or a general-purpose animation engine. Apply the useful design principle—give different concepts distinct motion grammars—to original video scenes: search can sweep a field, a connection can assemble links, and a solved idea can converge and settle. Do not place a persistent “AI is thinking” loader over unrelated footage. Use an orb only when its state metaphor precisely supports the narration, and give it a purposeful entrance and resolution.

For consistent brand work, create a small motion system: 2–3 movement types, a restrained palette, shared easing and line weight, a minimum readable hold, and a clear end state. Save it as a reusable project template rather than reusing the same complete animation in every video.

## Quality checks

- Each animated element has a script-linked purpose and a clear visual hierarchy.
- Motion changes the visual state in a meaningful way; no filler loops, random particles, or constant camera shake.
- Use easing, intentional overlap, and settled holds; avoid transitions that hide the subject or create disorienting flashes.
- Test at final delivery dimensions and on a phone-sized preview. Keep captions and critical UI readable.
- Verify the actual render at normal speed, especially the first/last frame and joins. A still frame cannot prove that motion feels smooth.
- Record third-party library versions and license notices in the project. Generated images, fonts, sounds, and model weights have separate rights.
