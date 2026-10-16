# Video Creation Workflow

Follow the full sequence below when the user asks for a finished video. Adapt the amount of work to the format, but carry each applicable stage through delivery. Ask a focused question only when an unresolved choice materially changes the video; continue other preparation meanwhile.

## 1. Define the purpose and feeling

Identify why the video should exist, who it is for, what viewers should feel or understand, and what they may do next. For personal stories, ask what makes the memory meaningful and let real details guide the treatment. For explainers, product, documentary, event, or client work, set the viewer outcome and evidence standard. Determine destination, runtime, orientation, resolution, language, narration, captions, branding, and deliverables. When comprehensive coverage would make one video unwieldy, use chapters or a series rather than silently dropping topics.

Choose a format that fits the story and viewing context. Estimate narration at a comfortable pace, then leave room for viewers to see, hear, or read the material. Verify current destination specifications when platform compatibility matters.

Before scripting or generating many assets, write a short visual direction that names the intended look, palette, typography, framing, motion, transitions, and sound approach. Explain why those choices fit this audience and subject. Review a representative frame or short scene at final playback size; refine the direction before producing the rest if it feels generic, hard to read, or mismatched. See [visual direction](visual-direction.md).

When the brief asks for custom motion design, a launch film, or an animated visual explainer, follow [motion-design production](motion-design-production.md) to author connected scene changes and render a pilot. No supplied footage is required for a concept that works as original animation. Choose the production route from the desired film, rather than defaulting every idea-only request to stock montage or simple diagram layouts.

## 2. Research and verify

Research when the video's subject, factual claims, or current details require it. Turn the brief into research questions, search appropriate sources, and prefer primary or authoritative sources. Browse when details are recent, unstable, specialized, or explicitly requested. Record source title, URL, access date, and the claim each source supports in the research ledger. Verify quotations, names, dates, numbers, and product behavior against the source.

Inspect and organize supplied material: video, audio, photos, scripts, browser captures, and documents. Build an evidence inventory. For recaps, adaptations, or dubs made from existing footage, use [the source-based video guide](source-based-video.md) to map source timecodes, speech, visible events, and selected edits before writing narration. For product tutorials, compare the live UI, approved help materials, and owner statements; note empty states, demo-only behavior, changing values, permissions, and discrepancies. For personal work, use specific real details and keep uncertain memories explicit. Separate verified facts, inference, and creative framing. Flag unresolved or contradictory claims; exclude them from narration until resolved. Research is not required for purely expressive work unless the user asks for it.

## 3. Write and fact-check the script

For audience-led work, connect audience need, title/poster, alternative hooks, first visual, source evidence, and the promised payoff before locking the script. Follow [audience, hooks, and retention](audience-hooks-and-retention.md) for the 21-category library and optional local plan check. A formula is a starting structure; keep the film's actual purpose and the user's tone primary.

Choose the right structure: a narrative arc, explainer sequence, demonstration, montage, interview, short-form hook/payoff, or another form that serves the brief. Write narration for speaking and separate stage directions from spoken words. For tutorials, explain purpose, sequence, expected state, and limitations. Avoid reading identifiers or sensitive values aloud. Keep each scene focused on one beat. For motion-led work, map each beat to a visible state change using the visual beat sheet; do not settle for a series of unrelated title cards when the brief asks for a performed, animated, or cinematic video.

Map facts in the script back to sources. Confirm the opening, story beats, transitions, ending, and call to action serve the stated goal. Estimate spoken duration and leave time for visuals to register. Create a storyboard, shot list, or scene plan. Use `../../../templates/scene-manifest.example.json` for multi-scene work. Track stable IDs, source assets, purpose, narration, visuals, captions, and timing through revisions. For every required line, claim, or key story beat, identify where it appears in the script and which scene proves or illustrates it; use the `../../../templates/coverage-matrix.md` for long or detail-heavy videos so omissions are visible before editing and during final review.

## 4. Source and prepare assets

For app walkthroughs, follow [app-capture.md](app-capture.md). For footage, review supplied material and log useful takes, action, sound, and source times. For photo stories, choose images that support the real story. For graphics or AI-generated video, use them for their intended illustrative or creative role and check continuity, text, anatomy, flicker, and artifacts. Preserve originals and provenance. Check permission and license for every external asset, font, voice, music cue, and model used. Do not make invented footage appear documentary or turn mock interfaces into product evidence.

Build a visual system that fits the tone and platform. Check graphics, subtitles, and logos at intended playback size and safe areas. Do not let overlays obscure faces, essential source text, or key visual evidence.

Before full production, make a rendered representative passage with real source action, narration, graphics, and a typical edit. For a footage-led promo, include two or more adjacent shots so rhythm, transitions, reframing, and sound can be assessed. Style frames may establish the look, but cannot replace this motion pilot. Review at delivery size; refine material findings before scaling. Preserve the user's existing creative choices and authorization.

## 5. Produce the video and audio

For narration or voiceover, use the user's specified voice or audition available candidates when the choice matters. Evaluate pronunciation, cadence, expression, pauses, and intelligibility. Do not promise natural-sounding generated speech without listening. Preserve authentic source audio when it matters to the story.

For a new user with no saved voice choice who will use Pocket TTS for English narration, ask who they want on voiceover and prepare the complete 21-preset audition page with `scripts/audition_pocket_voices.py`. Open/show `index.html` and wait for their choice before generating full narration. The page plays the same sample line for every voice, links each source/license, and flags noncommercial-only presets. Respect a direct user choice without making them audition first.

For presenter-led, talking-head, or lip-synced videos, lock the approved narration before planning final cuts, captions, or generated presenter footage. Check the recorded/generated audio against the approved script using speech recognition when available or careful listening; fix meaningful omissions, additions, names, numbers, and pronunciation before editing. Use actual audio and clip durations as timing evidence. Follow [the presenter and talking-head workflow](presenter-workflow.md) for pilots, continuity, synchronization, and resumable production records.

For Piper or another local TTS engine, select an exact model and check both its model terms and underlying dataset terms for the intended use. An earlier voice audition does not establish commercial rights. Keep selection configurable and exclude model files from the repo.

Synthesize in phrase- or scene-sized units when this makes corrections and timing manageable. Keep pronunciation notes in the project. Audition a representative passage before batching the full script. Leave room around speech edits and preserve the final word.

Use music and sound effects only when supplied or authorized. Check their terms for the planned use. Mix speech clearly and keep effects subordinate to the story.

## 6. Edit, review, and deliver

Assemble and edit shots, source audio, narration, graphics, titles, transitions, and music into a coherent timeline. Keep speech and visible action synchronized where viewers expect it. Use cutaways only when they support the same idea. Set pace to the material; avoid effects that distract. Respect aspect ratio and caption safe areas. Keep a timeline or manifest that makes revisions reproducible.

Generate captions from final audio timing. Keep phrases readable, align their boundaries to speech, and leave complete words at cuts. Retiming or replacing a voice line requires regenerating affected captions and scene duration.

Follow [the editing skill](../../editing-videos/SKILL.md) and its review checklist. Treat the first render as a review candidate. Check that the file plays, meets the requested duration and frame size, includes every required line and scene, keeps text legible, and has visuals that change when the brief calls for motion. Review the creative quality as well as technical correctness, log issues, revise, and re-export until material issues are resolved. Deliver the actual final video and requested sidecars/project files, with a short record of research sources, tool/asset rights, checks performed, and known limits. Publishing or uploading remains a separate user request.
