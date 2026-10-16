---
name: creating-videos
description: Use when a user wants a new video made from an idea, research, supplied footage, a screen recording, a reference, or generated assets. Use for end-to-end production, including when raw footage is provided; use editing-videos when they only want an existing cut changed or reviewed.
---

# Creating Videos

Own the full lifecycle: research when needed, concept and script, source and create assets, produce footage/audio, edit the video, review it, and deliver the final export. Do not stop after a script, storyboard, or rough cut when the user asked for a finished video. Read [the production workflow](references/production-workflow.md), then load only the specialist guides that fit the request:

- New idea, factual topic, or current claims: [research and scripting](references/research-and-scripting.md).
- Audience-led explainers, promos, channel videos, strong openings, title/thumbnail planning, Shorts, or learning from retention: [audience, hooks, and retention](references/audience-hooks-and-retention.md). Use its 21-category library to consider suitable openings and connect the chosen promise to actual visual proof and a script payoff; the local workbench checks plan structure without predicting popularity.
- Supplied footage to recap, adapt, or dub: [source-based video](references/source-based-video.md).
- Supplied reference video to analyze: [reference-video analysis](references/reference-video-analysis.md).
- Find reusable visual concepts or adapt public motion prompts: [reference library workflow](references/reference-library-workflow.md). Search the local collection snapshot, inspect a relevant prompt and accessible examples, then write a treatment for this subject before rendering. Use it when no suitable visual direction is established; keep approved creative choices primary.
- Presenter or talking head: [presenter workflow](references/presenter-workflow.md).
- App or website walkthrough: [app-capture guide](references/app-capture.md), including fixed-scale UI framing and readable scroll captures.
- Animation, generated visuals, or a motion-led treatment: [creative modes](references/creative-modes.md) and [visual direction](references/visual-direction.md).
- Polished custom motion design, an animated launch film, or a graphics-led video without camera footage: [motion-design production](references/motion-design-production.md). Author a specific visual concept with connected scene changes; use its editable Canvas study and local HTML renderer or HyperFrames to execute. Do not default to the lightweight diagram layouts for this brief.
- Promotional, brand, social, or footage-led work: [visual storytelling](references/visual-storytelling.md) and [stock sourcing](references/stock-footage.md). Choose an execution route with [production tooling](references/production-tooling.md).
- Original custom animation: [motion graphics with p5.js/p5.brush](references/motion-graphics.md). Voiceover, voice synthesis/cloning, and score: [voice and music](references/voice-and-music.md), with separate checks for code, model-weight, speaker-consent, and music rights.
- For polished HTML/SVG/React motion graphics, use [Motion library for video graphics](references/motion-library-workflow.md). Motion adds animation controls; pair it with a frame-seekable local renderer, since the existing automatic Python renderer does not use Motion and Motion itself does not export finished videos.
- For local, graphics-led or hybrid HTML-animation videos, read the optional [HyperFrames workflow](references/hyperframes-local-workflow.md). It includes a story-led catalog search and a reusable per-item rights review template. Keep the Node/FFmpeg project local and choose it alongside the existing footage composer based on the media and timeline needs.
- Idea-only work with no supplied footage and a no-paid-services requirement: choose [motion-design production](references/motion-design-production.md) for custom animation, or [automatic free production](references/automatic-free-production.md) for a montage with sourced public footage and simpler diagrams. The agent must research, script, plan relevant visuals, inspect the actual rendered media, and repair problems; neither route guarantees editorial quality automatically.

For promos, social ads, and other footage-friendly videos, prefer a footage-led or mixed visual plan: use verified free clips for real-world actions and environments, real product captures for product behavior, and original graphics for abstract ideas that camera footage cannot explain. Each clip query must name a concrete subject and action tied to its narration beat. Reject clips that only share a keyword or mood; do not fill a gap with generic stock.

Use [the editing skill](../editing-videos/SKILL.md) and its review checklist for post-production. When the user only wants changes to an already assembled video, start with the editing skill instead.

Check the available browser, research, capture, audio, editing, and rendering tools early. Choose a feasible route based on actual access and capability. Continue useful stages if a tool is missing; clearly state the blocker and provide the best available deliverable without claiming that an uncreated video is finished.

For a film-like or footage-led brief, plan shots from actual source media before building layouts. A succession of text cards, screenshot pans, or a moving progress bar does not fulfill that brief. Review a rendered passage containing real action and at least one edit before scaling production. Static frames establish art direction; they do not establish motion or editorial quality. Tutorials and diagrams may hold when viewers need time to understand them.

For narrated promos, plan several distinct, script-matched visuals within longer sentences. Do not reuse one background clip under a run of changing titles or screenshots. Describe each shot's visible action and why it supports that precise beat; check the adjacent sequence for repeated source, screenshot, crop, and composition. Use deliberate phrase/action changes at a pace viewers can follow, while allowing interfaces and disclosures time to read. See [visual storytelling](references/visual-storytelling.md).

For a selected short-form video, default to a new relevant scene or clearly changed visual state every 2–3 seconds. Split long narration into shorter beats and build enough distinct visuals to hold that rhythm; do not pad time with a repeated clip or static card. Permit longer holds only for an essential readable moment or real action, and record why in the plan. The automatic-free renderer enforces this short-form limit unless the visual has a specific `hold_reason`.

Before rendering any video, complete the format-aware engagement pass in [visual storytelling](references/visual-storytelling.md): fit the opening, structure, pace, visuals, sound, and ending to the audience and intended outcome. Do not assume faster cuts, narration, music, stock footage, or a hook formula improves every format. Use 2–3 second visual changes as a short-form starting point only; let tutorials, interviews, documentaries, personal stories, and other forms breathe when understanding or emotion needs time.

Prefer ElevenLabs for generated narration when the user selects it, approves sending the script to the hosted service, and configures `ELEVENLABS_API_KEY` locally. Never ask the user to paste a key into chat, a prompt, a plan, `runtime.json`, or Git; ask them to configure it through a local secret store/environment. Have a new user choose a voice and set `ELEVENLABS_VOICE_ID` or pass `--voice-id`. ElevenLabs may consume free quota or paid account credits, so disclose this and get approval before synthesis if usage is not already authorized. If the user declines or has no key, use Pocket TTS; if the API fails, explain the error and offer the local fallback instead of silently switching providers. For a new Pocket user without a voice choice, generate the 21 English audition samples using `scripts/audition_pocket_voices.py`, show/open its `index.html`, and wait for their selection. Use a voice already selected by the user without making them audition again. Make voice/model/data terms visible and preserve required credits; `cosette` and `jean` Pocket presets are noncommercial-only.

## Required production record

Maintain these project artifacts as they become available:

1. A brief describing purpose, audience, intended feeling or viewer outcome, destination, length, format, style, and call to action.
2. Research notes and a source ledger for factual or current claims; clearly mark when research is not needed.
3. A checked script, treatment, storyboard, and shot/scene plan suited to the format.
4. An asset/rights record, production timeline, and edit manifest when useful.
5. A reviewed final export, editable project, caption/transcript sidecars when useful, and concise review notes.

## Working rules

- For personal stories, understand the human meaning before choosing pace, music, or visual effects. Keep memories truthful and do not invent events.
- For factual, documentary, product, or client work, separate verified facts from inference and flag unresolved claims. Do not fabricate evidence, interfaces, testimonials, or quotations.
- Match the concept to the actual source material. Generated visuals are illustrative unless verified; do not present them as captured evidence.
- Protect privacy and identity. Use approved material and permissions for people, voices, music, fonts, stock, and generated assets.
- Prefer local/free tools when they meet the brief. Confirm actual provider capability, cost, access, and rights before using them.
- Never start a paid job, subscription, or trial without the user's explicit approval.
- Creating a video does not authorize publishing, sending, or uploading it.
- Review the rendered export with the editing skill's checklist before delivery.
- Treat review as an iteration loop: inspect every shot's sampled frames and the full cut at normal speed, record concrete issues, repair them in the script/plan/assets/edit, and render again. Continue until no blocking visual, narrative, rights, caption, or audio issues remain. Automated checks can establish technical properties; they cannot certify that the story is excellent. If the host cannot inspect video/audio, state that limitation instead of calling the result fully reviewed.

## Typical deliverables

Deliver the requested format plus the editable project, captions/transcript, asset/source notes, and review notes when useful. Keep temporary renders and source assets in a separate project directory. State the actual review method and any unavailable checks.
