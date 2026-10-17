# Cinematic motion editing for supplied footage

Use this route when a user wants an existing video, interview, product demo, or short-form edit to feel more cinematic, dynamic, or reference-inspired. The goal is a coherent visual story built around the real footage—not a slideshow, a stack of effects, or a copy of someone else's style.

This guide extends the [footage-first edit workflow](raw-footage-workflow.md), [shot composition](shot-composition.md), [motion graphics guidance](../../creating-videos/references/motion-graphics.md), and [motion-design production](../../creating-videos/references/motion-design-production.md). Read the first for source review and reversible cutting; use this guide to bridge that edit to an original motion treatment.

## 1. Diagnose the story and the reference

- Review the full source with sound before proposing a treatment. Identify the audience, purpose, emotional turn, strongest spoken phrases, useful gestures, screen actions, and footage limitations. Preserve meaning, factual claims, speaker identity, and any requested wording.
- If the user gives a visual reference, describe its transferable mechanisms (such as recurring motifs, kinetic type, scene changes, contrast, or transitions). Do not copy its characters, artwork, composition, script, or distinctive frame sequence. Apply those mechanisms to the user's subject and brand.
- State the practical limits before committing to an effect: available footage, aspect ratio, local renderer/editor capability, compute time, and any stock or generative source permissions. Prefer local/free methods when they meet the brief. Never imply Google Flow, stock search, a paid API, or advanced tracking/rotoscoping is available unless it is actually connected and authorized.

## 2. Write one visual treatment

Before styling the whole timeline, define a one-page treatment:

| Decision | Choose |
| --- | --- |
| Viewer takeaway | One sentence the edit should leave with the viewer |
| Visual metaphor or motif | A meaningful object, shape, gesture, or graphic state that can evolve with the story |
| Type system | One display face and one readable supporting face, with a clear hierarchy and caption treatment |
| Palette and texture | A small, subject-appropriate set of colors and a restrained surface treatment |
| Motion grammar | A few repeatable moves (for example, follow, reveal, pass-through, scale settle, or match move) and their easing |
| Sound character | Dialogue-forward mix, musical energy, ambience, and a small set of motivated effects |

Choose visual language for this story rather than applying a default “viral” preset. Use readable type and safe margins at the final viewing size. Motion should have an entrance, a legible settled state, and an exit or handoff; avoid continuous decorative movement. Treat captions for accessibility separately from short, expressive headline words.

## 3. Map the words to changing visuals

Create a visual beat sheet before adding polish. For each important line or story beat, record its time, exact phrase or idea, purpose, source shot/action, added graphic or insert if needed, motion, transition into the next beat, and why that visual fits. Cover the opening, each story turn, proof or demonstration, and the call to action. Do not force one visual per sentence: a clear action can span several lines, while a long line may need more than one visual change.

Use this priority order for each beat:

1. Show the relevant action or detail in the user's own footage.
2. Reframe, cut to a different take, or add a restrained camera move when the source can support it.
3. Add a designed graphic, typography, tracked callout, split view, diagram, or short authored animation that explains the exact idea.
4. Add a directly relevant, rights-checked stock or generated insert only when it contributes information or emotion the source cannot provide.

Every added visual needs a specific relationship to the words. Avoid generic laptop, office, city, or smiling-people footage as filler. Do not hide missing story coverage behind random motion or claim a generated illustration is real evidence. If an essential moment has no appropriate source, flag the gap and propose an honest graphic or request a suitable asset.

## 4. Design edits and motion as a connected sequence

- Build a rhythm with changing shot scale, composition, action, and information density. Change visuals when the meaning turns or the eye needs a new point of attention; do not cut at a fixed interval or flash frames just to appear energetic.
- Let footage and graphics share the frame deliberately. Use masks, foreground/background separation, a graphic that grows from a real object, a label that follows a demonstrated control, or a diagram that resolves into the next shot only when the source supports that relationship. If tracking or roto is unavailable, choose a simpler fixed graphic rather than faking a lock-on.
- Make transitions carry meaning: match action or shape, follow a hand/object, pass through a mask, use a short directional blur, or cut cleanly at a spoken or musical accent. Most cuts need no transition. Build outgoing and incoming states together, and keep words readable across handoffs.
- Use motion graphics to emphasize hierarchy and story: scale, position, crop, opacity, mask, line drawing, path movement, depth, and restrained parallax. Use a deliberate small motion vocabulary, with varied composition and contrast. Avoid piling on bounce, glow, particles, camera shake, and wipes in every scene.
- Protect the speaker's face, gestures, and emotional pauses. Do not cover essential source detail with captions or graphics. Keep dialogue intelligible; duck music under speech and sync effects to visible events without making every movement noisy.

For supported local timelines, capture each planned visual as its own meaningful beat in the [shot-composition manifest](shot-composition.md). For custom authored compositions, use the local techniques and renderer guidance in [motion-design production](../../creating-videos/references/motion-design-production.md). Use a full editor for tracking, rotoscoping, advanced compositing, dialogue repair, or timing that the simple renderer cannot perform.

## 5. Prove the treatment in a representative pilot

Before applying a new treatment everywhere, cut and render a representative 6–12 second passage that includes real footage, speech, at least one meaningful visual change, the intended typography/graphics, a transition, and the proposed sound balance. Choose a passage that tests the hardest part of the brief, not merely the easiest title card.

Review at the actual destination size and normal playback speed. Ask:

- Can the viewer understand the spoken idea and the visual relationship without pausing?
- Does the sequence show real source action as well as designed elements, where useful footage exists?
- Does every insert, word, movement, and sound support this beat?
- Is the type readable, correctly timed, in safe areas, and clear over the image?
- Does the motif evolve, and does each transition connect the outgoing and incoming thought?
- Are the speaker's face and meaning preserved? Does the mix keep dialogue clear?
- Does it feel purpose-built for this subject, or like a reusable template with changed text?

Revise the treatment if any answer exposes a problem; do not propagate a weak pilot. Once approved, apply the visual system across the edit while varying shot choices and composition to fit each beat. Review the whole encoded video with sound and use the existing delivery gate. Preserve the source, beat sheet, timeline/edit data, rights evidence, and review notes so the result can be revised.

## Common failure modes

| Failure | Correction |
| --- | --- |
| One talking-head angle carries the whole edit while words change | Find meaningful source actions and angles; add a subject-matched graphic only where it advances the point |
| Every line gets a new random stock clip | Keep a beat-to-visual reason for each change; reuse a motif only when its state evolves |
| Type fills the screen but hides the person or source detail | Establish hierarchy and safe regions; let the footage remain a primary visual |
| Every cut has a flashy transition | Reserve transitions for conceptual or action handoffs; use clean cuts for the rest |
| The reference's distinctive look is copied literally | Extract broad motion principles and author original assets, layouts, color, and story |
| A successful render is called professional without playback review | Watch the full export at intended size and listen to it; technical validity is not creative approval |
