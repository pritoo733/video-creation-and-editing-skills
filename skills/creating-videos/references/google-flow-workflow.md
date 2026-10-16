# Google Flow clip workflow

Use Google Flow as an optional hosted source for custom, narration-matched video clips. Flow is operated manually in its browser app; this repository does not call a Flow API, automate account access, or generate clips on its own. After the user creates and downloads clips, the local workflow can validate the plan structure, keep provenance, build a storyboard, and assemble those clips with local editing tools.

## Choose Flow only when it helps the story

- Plan each generated clip against one specific narration beat. State the visible action and why it illustrates that exact line. Generate distinct shots for distinct beats; do not stretch one Flow clip across unrelated claims.
- Use Flow for illustrative B-roll, stylized reconstructions, environments, or actions that cannot be captured locally. Use genuine screen recordings for product behavior, and sourced documents or verified captures for facts, figures, endorsements, customer outcomes, or other evidence.
- For a continuous character, location, or product concept, keep a short continuity note and reuse only approved reference ingredients. Review each output for changed identity, setting, wardrobe, objects, text, hands, logos, and other discontinuities.
- Avoid prompting the model to render readable titles, captions, logos, UI, prices, or disclosures. Add verified text locally during editing.
- For short-form work, plan changes at the pace chosen in the brief (usually a new relevant visual every 2–3 seconds). A generated Flow clip may be longer than its final edit interval; log the source in-point and use only the moment that supports the narration.

## Budget, account, and privacy checks

1. Flow is a hosted service. Prompts and uploaded reference media are sent to Google. Before using it, check that the user is comfortable with that processing and has approved the particular reference media; never upload confidential, personal, or customer content without permission.
2. The free-production route may use only the account's currently available **daily free credits**. Check the balance, active model, generation settings, and displayed per-generation cost in Flow immediately before confirming. These values, eligibility, peak-hour availability, supported durations, and model options can change. Never buy credits, subscribe, upgrade, or silently switch to paid credits. If free generation is unavailable, continue with an approved local capture, locally generated motion, or appropriately licensed public footage.
3. Google currently documents 50 daily credits for eligible non-subscribers, but availability and model costs vary. Treat the live account UI as the cost authority; do not hardcode that balance or assume every creator has the same allowance. See [Google Flow credit guidance](https://support.google.com/flow/answer/16526234).
4. Some locations or account tiers require a visible Flow/Veo watermark; Flow generations also carry invisible SynthID provenance. Inspect the current account setting and each exported clip. Keep both visible and invisible provenance marks intact. Do not crop, blur, cover, replace, or otherwise remove them. Where a visible mark appears, keep the entire Flow frame in view (the compositor uses `contain`) and confirm the result is appropriate for the intended destination before rendering.
5. Do not label Flow output “royalty-free,” public domain, or rights-cleared by default. Review the current Google terms, the intended commercial use, any uploaded/reference media rights, and any identifiable people, marks, or property. Record unresolved rights questions and do not publish until they are addressed. Google requires the SynthID provenance mark to remain; see [Flow asset guidance](https://support.google.com/flow/answer/16935308) and [Google Terms](https://policies.google.com/terms?hl=en-US).

## Generate and export clips

1. Finalize the brief, script beats, visual direction, and shot list before using credits. Copy [`../../../templates/google-flow-shot-plan.md`](../../../templates/google-flow-shot-plan.md) into the project and prepare a small representative batch first.
2. In the logged-in Google Flow desktop app, create/open a project. Before each generation, inspect the selected model, aspect ratio, duration, prompt settings, current cost, and account balance. Model capabilities and supported lengths vary; use the settings shown in Flow rather than assuming a fixed model or clip length. Google's current [model and feature guide](https://support.google.com/flow/answer/16352836) describes the available controls.
3. Write one shot prompt with a concrete subject, one main visible action, setting, framing, camera movement, light, and continuity details. Include the desired aspect ratio and composition through Flow's controls. Describe a real-looking scene only when the script calls for illustrative B-roll; never ask Flow to invent a real customer, factual event, product result, or captured product interface.
4. Generate the pilot, inspect the full clip, and check narrative relevance, continuity, motion artifacts, text/logos, watermark visibility, and framing. Keep or regenerate only when the mismatch is material and free credits remain. Do not create a large batch before reviewing the pilot.
5. Download the chosen clip from Flow as an MP4. See [Google's download steps](https://support.google.com/flow/answer/16935308). Put the original file under the project folder at `assets/google-flow/`. If you use Google Takeout, keep the paired metadata JSON beside the clip and point to it in the shot plan; Flow Takeout can include prompts and generation settings. Do not put the clips, reference media, or account exports in this skills repository.
6. Record the exact prompt, model, aspect ratio, generated duration, credits consumed, free-credit basis, watermark state, file name, and (if available) Flow metadata file in the project plan. Keep exported originals unchanged; the local renderer stages a copy in the output project and records its SHA-256 in `google-flow-assets.json`.

## Add Flow clips to a local plan

The local renderer accepts a `google_flow` visual when the downloaded MP4 is inside the project directory and the generation record is complete. Example:

```json
{
  "kind": "google_flow",
  "path": "assets/google-flow/closing-aerial.mp4",
  "action": "A slow aerial move reveals a small neighborhood street at sunrise",
  "why_it_fits": "The narration moves from a single decision to the broader community it can affect",
  "generation": {
    "prompt": "Slow cinematic aerial glide above a quiet American neighborhood street at sunrise, natural warm light, no readable signs or logos, steady camera, realistic illustrative B-roll",
    "model": "Exact model name shown in Google Flow",
    "aspect_ratio": "16:9",
    "duration_seconds": 8,
    "credits_used": 10,
    "credit_source": "free_daily",
    "visible_watermark": "present",
    "metadata_file": "assets/google-flow/closing-aerial_metadata.json"
  }
}
```

`generation.metadata_file` is optional if no paired metadata file was exported. The renderer requires `credit_source` to be `free_daily`, copies the clip and metadata into the output project, retains the full frame so watermarking remains visible, and adds a provenance record to the storyboard, production log, `CREDITS.md`, and `google-flow-assets.json`. It rejects missing/out-of-project clip paths and repeated identical Flow clips. This is local clip ingestion, not automated access to Flow.

Render with the normal local command after installing the required runtime:

```powershell
.\.video-tools\Scripts\python.exe skills/creating-videos/scripts/auto_produce.py path\to\project\plan.json --output path\to\project\output --runtime .video-tools\runtime.json --draft-only
```

Review `storyboard.html`, including the start/middle/end source frames for every Flow clip. Confirm each frame supports its narrated beat, check for misleading detail and watermark visibility, and revise the edit interval or shot before final rendering. Use the local dashboard to browse the final project; source clips inside `assets/` are not counted as completed videos, and the Flow clip count and manifest are shown separately.

## Required final checks

- Listen/watch the full final cut and verify every Flow visual matches its exact narration beat.
- Confirm the source is illustrative, not presented as a real customer, product UI, record, statistic, or documentary event.
- Confirm all Flow provenance marks remain visible/intact; do not mask them with titles, captions, crops, or overlays.
- Review current account costs and Google terms for the intended use; retain any Flow source metadata and the recorded prompts with the output.
- If the watermark or other Flow artifact makes the clip unsuitable for the requested channel, replace it with a suitable locally captured, locally animated, or rights-checked public source. Do not spend additional credits automatically.
