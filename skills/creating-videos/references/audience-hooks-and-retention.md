# Audience, hooks, packaging, and learning from results

Use this guide for audience-led explainers, promotional videos, tutorials, social clips, or channel work where the opening promise and viewer follow-through matter. Adapt it to the destination and the user's intent. A personal memory film, a quiet artistic piece, and a detailed training module may need a very different opening from a short product ad.

## Start with a viewer and a feasible topic

Use the existing brand or owner preferences, supplemented by [the audience and voice profile](../../../templates/audience-and-voice.md) when helpful. Writing cadence is separate from the narration speaker/model. Reuse the chosen voice and pronunciation notes. If no samples exist, infer a reasonable starting tone from the brief and state it; do not block production waiting for three videos.

For an open topic brief, propose a few ideas with a clear viewer need, visible proof or illustration, available source material, and a realistic production cost. Prefer a useful topic that can be shown honestly over an ambitious claim without evidence. Size a series or calendar to actual capacity and existing material; there is no universal upload frequency or best publishing day.

When researching comparable videos, record publication date, format, audience, and what is publicly observable. Comparing a video's views with the same channel's typical comparable uploads can help surface ideas, but account for video age, traffic sources, and small samples. Popularity does not prove that a hook formula caused the result. Use other films for structural analysis; reuse their footage, music, or artwork only when separately cleared.

## Treat the title, thumbnail, and opening as one promise

Write a viewer promise before drafting. For a YouTube-style package, develop the title, thumbnail concept, first spoken line, and first visual together. A website promo may instead use a headline, poster, and opening action. Each should support the same outcome while contributing useful information. Deliberate repeated brand names can be valid; repetition is a review prompt, not an automatic defect.

Inspect the actual destination layout at a small viewing size. Keep key words early and make the subject recognizable in the image. Avoid treating a fixed character count or thumbnail word count as a universal platform limit. Verify current destination requirements when preparing publication assets. Do not promise a test, result, price, speed, or product capability that the video cannot demonstrate accurately.

## Choose among 21 hook categories

The bundled [21-category library](../assets/hook-formulas.json) adapts the categories in `youtube-agent-skill` with original prompts, proof requirements, visual opening suggestions, and failure risks. Each is an option for structuring an opening; a film does not need all 21. Read the whole selected entry before using it.

Usually draft three to five genuinely different approaches, adjusted to the task. For example, compare a concrete question, an immediate artifact reveal, and a real before/after. Choose using audience fit, truthfulness, available visuals, readability, tone, and how naturally the script can deliver the promise. A short video may establish the premise in its first few seconds; a complex tutorial may need more setup. Do not impose a fixed 15-second hook on every format.

Numerical claims need context and a source. Experiments must have actually happened. Before/after needs both real states. A deadline must be real and current. A comparison can fairly conclude with tradeoffs. A restrained, truthful question can be stronger than an unsupported dramatic warning. Do not add fear, inflated numbers, or absolute language to improve a score.

Use the free local workbench to inspect the library or check an agent-authored package:

```sh
python skills/creating-videos/scripts/hook_workbench.py --list
python skills/creating-videos/scripts/hook_workbench.py skills/creating-videos/assets/script-package.example.json --output working/hook-review.json
```

The [sample package](../assets/script-package.example.json) connects three candidate hooks, evidence records, one selected opening, timed script beats, a visual action per beat, and an explicit payoff. The LLM writes this package from the user's brief; do not ask the user to hand-author JSON. When copying it into a project, replace the example subject and update evidence paths relative to the copied file. A local evidence path is checked for existence; URL records remain offline declarations and must actually be reviewed by the agent.

The workbench checks structure, selected-hook/script consistency, payoff references, source-record completeness, timing continuity, estimated spoken length, and simple packaging wording. Rejected hook candidates may remain in the record with their defects, while a defective selected hook fails the review. A technically valid plan still requires editorial review. The tool does not predict views, score artistic merit, verify the truth of a source flag, or decide whether a visual genuinely proves a claim.

The script package is a preproduction record, not an input schema for `auto_produce.py` or the shot composer. Translate its selected script and visual actions into the chosen renderer's existing manifest, retaining the beat IDs, source references, opening promise, and payoff. After timing or copy changes, reconcile both records. Word-based timing estimates need adaptation for languages with different word boundaries; use measured speech as the final authority.

## Carry the promise through the film

Make the opening show enough of the real result to establish trust. Map each promised item to a scene, source, and explicit payoff. For each body beat write what changes on screen, what the viewer learns, and why the next beat follows. Use actual demonstrations, relevant footage, original diagrams, or [custom motion design](motion-design-production.md) as the story requires. An attractive title card alone is not evidence for the claim.

Write spoken copy in the owner's voice, then estimate delivery time using an appropriate speaking rate. Replace estimates with measured narration timing before the final edit. Preserve breaths, reading time, necessary qualifications, and visual demonstration time. Deliver the promised answer or artifact clearly; close with an appropriate next action. Avoid adding multiple unrelated asks.

Continue through [the production workflow](production-workflow.md) and [editing/review](../../editing-videos/SKILL.md). Transcript-based cut suggestions must be checked against picture and sound: a speech gap may contain a useful silent demonstration. Keep cuts reversible, inspect joins, and regenerate captions after timing changes.

Prepare titles, posters/thumbnails, descriptions, transcript/captions, and chapters when useful to the destination. Link or include any promised resource. Verify chapter and upload requirements from current official documentation before delivery. Publication and sending messages are separate actions requiring user authorization; this guide and its tools do neither.

## Reuse long material as self-contained short videos

Inspect the actual source and timed transcript for a moment with an understandable opening, a meaningful development, and a complete resolution. Preserve qualifications and context so the short does not change the original meaning. Record its source interval and what would be lost in a crop. A new opening line can provide missing context, but must not fabricate a claim or imply that edited words were spoken verbatim.

Build the vertical or square treatment for its destination, retime captions, and inspect essential evidence after reframing. A loop is optional; use it only if the ending remains honest and understandable. Render and review the short as its own deliverable. Do not assume a fixed clip duration applies to every platform or request.

## Learn from real outcomes when data is available

Use authorized exports or user-supplied analytics. If no data is available, keep observations as hypotheses; do not invent a retention curve or benchmark. Normalize retention into an explicit local CSV with `seconds,retention_percent` columns. Convert fractions or percent-of-duration axes deliberately using the actual runtime; do not guess units. Retention above 100 can be valid for repeated viewing.

```sh
python skills/editing-videos/scripts/analyze_retention.py project/retention.csv --plan project/script-package.json --output project/retention-review.json
```

This stdlib-only helper reports the observation window, percentage-point changes, the largest declines between samples, and overlapping planned beats. It reports the first-30-second drop only when the samples cover that interval; it states when linear interpolation was used. A sampled interval cannot locate an exact departure frame. It makes no universal healthy/unhealthy verdict and does not decide why viewers left.

Inspect the corresponding picture, narration, captions, audience expectation, and traffic mix before recommending a change. An early decline could reflect a mismatch with the title, an unclear demonstration, audience selection, or other factors. A replay spike may mean interest or confusion. Compare matched formats and audiences when possible. Record one useful hypothesis and the next change to test; retain the previous version and actual results so learning improves later projects.

## Source and adaptation boundary

Reviewed `Jakeschincariol/youtube-agent-skill` at commit `a2feb2104981a375ffd4f87ee04f4f5344ac43c6` on 2026-10-16: its README, 21-hook library, scripting/packaging/voice guidance, transcript editing, planning, Shorts, and retention workflow/tools. Its MIT notice is retained beside the adapted category library. The helpers and guidance here are original implementations. No upstream executable is installed or required.

Useful adopted ideas are audience continuity, alternative openings, packaging as a unit, explicit payoff mapping, transcript-grounded editing, context-preserving Shorts, and a feedback loop. We do not adopt its fixed upload schedule, universal title/thumbnail limits, mandatory sample requests, model-specific paths, or causal conclusions from a retention curve.

- [Upstream project](https://github.com/Jakeschincariol/youtube-agent-skill)
- [Pinned 21-hook source](https://github.com/Jakeschincariol/youtube-agent-skill/blob/a2feb2104981a375ffd4f87ee04f4f5344ac43c6/skills/yt-script/hooks.json)
- [Upstream MIT license](https://github.com/Jakeschincariol/youtube-agent-skill/blob/a2feb2104981a375ffd4f87ee04f4f5344ac43c6/LICENSE)
