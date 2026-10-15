# Production Workflow

## 1. Define the viewer's outcome

Write one sentence describing what a viewer should be able to explain or do after the video. Name the audience and each distinct role. Set a target runtime, aspect ratio, resolution, language, narration style, captions, branding, and requested deliverables. If the brief asks for comprehensive coverage, group material into chapters and role-based paths instead of reading every control without context.

Estimate narration using a comfortable pace (roughly 125–155 spoken words per minute), then add time for screen reading and transitions. A long training video may be useful, but split it into chapters and consider a short overview plus the complete reference walkthrough. Do not shorten requested coverage silently.

## 2. Ground the script and scene plan

Build a feature inventory from accessible product help, authorized browser inspection, provided documents, and genuine captures. Record where each statement came from: observed UI, written guidance, owner-approved claim, or inference. Note empty states, demo-only behavior, changing values, permission differences, and discrepancies. Ask only for decisions that materially change what can be shown or claimed; continue independent capture planning while they are unresolved.

Write narration in plain spoken language. Explain what an area is for, who uses it, the sequence of actions, what to verify, and what the action does or does not establish. Do not read sample names, balances, rates, IDs, addresses, or contact details aloud. Put stage directions and overlays outside spoken copy. Keep each scene focused on one task or idea.

Create a storyboard and capture list before recording. Use the example structure in `../../../templates/scene-manifest.example.json`. Each scene should have an ID, chapter, short title, source asset, purpose, narration, key notes, and transition/capture cues. Keep the scene names stable so edits do not break timing references.

## 3. Capture and prepare assets

For app walkthroughs, follow [app-capture.md](app-capture.md). Capture browser screens at a readable scale with deliberate navigation and pauses. Save actual captures as lossless PNG when feasible; preserve source files and their context. Zoom details from genuine captures without inventing or rewriting UI. Use callouts to direct attention without hiding important controls or notices.

Create a consistent title card, scene header, and lower-third style. Keep overlays within safe margins and test them at the intended playback size. Distinguish illustrative/generated visuals from real product captures where a viewer might confuse them.

## 4. Audition and synthesize narration

If the user specifies a voice, use it as the candidate and audition representative product names, acronyms, numbers, and longer sentences. If not, present a few locally available voice options and ask only when the voice materially affects the intended audience or brand. Evaluate pronunciation, cadence, warmth, breath/pause behavior, and intelligibility; do not promise that generated audio is non-robotic without listening review.

For Piper, select the exact model intentionally (for example, Lessac `en_US-lessac-medium` was used in the source project). Check the model and underlying voice dataset license before use, especially for commercial or public distribution. Keep the voice model configurable and do not commit model files to the repo.

Synthesize in sentence or phrase-sized units so pronunciation, pause timing, and captions can be corrected without regenerating all scenes. Apply a small natural pause between phrases and a clear hold after the final sentence. Keep pronunciation substitutions in a project lexicon. Audition a complete representative scene before batching the full script; repair any strange acronym or proper-name pronunciation first.

## 5. Assemble the timeline

Map each scene's audio duration to its screen visuals. Use a readable overview frame, then a genuine close-up or alternate approved screenshot when detail matters. Hold long enough for the viewer to inspect the page; change visuals to match the point being spoken. Keep speech continuous across B-roll only when the sentence remains coherent. Avoid decorative zooms, transitions, or music that compete with instruction.

Generate captions from final audio timing, not estimated script length. Keep phrases readable, align their boundaries to speech, and leave complete words at cuts. Retiming or replacing a voice line requires regenerating the affected captions and scene duration.

For the detailed review, export parameters, and repair loop, follow [the editing skill](../../editing-instructional-videos/SKILL.md) and its review checklist.
