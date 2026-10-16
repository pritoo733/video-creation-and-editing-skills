# Google Flow shot plan

Use this as a per-project planning and provenance record. Keep it beside the script/plan and keep exported source clips under `assets/google-flow/`. Never store account credentials here.

## Story fit and budget

- Video purpose and audience:
- Destination and format:
- Why Google Flow helps this story:
- Hosted-processing approval confirmed:
- Free-credit balance checked in Flow at:
- Rule: use daily free credits only; stop if Flow requires an upgrade or paid credits.
- Watermark setting and destination suitability checked:
- Reference media approved for upload:

## Shot inventory

| Shot ID | Script beat | Visible action | Why it supports that line | Prompt | Model | Ratio / duration | Credits (free daily) | Watermark | Exported file | Metadata JSON | Review result |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| F01 | | | | | | | | | | | |

## Local renderer visual record

Copy the following shape into the relevant `visuals` array in `plan.json` for each selected Flow clip. Keep paths relative to the project folder. The model and credit values below are examples; enter the values Flow actually shows for your generation.

```json
{
  "kind": "google_flow",
  "path": "assets/google-flow/shot-f01.mp4",
  "action": "Describe the visible action in the exported clip",
  "why_it_fits": "Tie this image to a specific narration phrase or story beat",
  "source_in": 0,
  "generation": {
    "prompt": "Paste the exact prompt submitted to Flow",
    "model": "Veo 3.1 Lite (example; verify in Flow)",
    "aspect_ratio": "16:9",
    "duration_seconds": 8,
    "credits_used": 10,
    "credit_source": "free_daily",
    "visible_watermark": "present",
    "metadata_file": "assets/google-flow/shot-f01_metadata.json"
  }
}
```

Remove `source_in` to let the local runner select a suitable source interval. Remove `metadata_file` if no paired metadata export exists. `visible_watermark` accepts `present`, `not_visible`, or `unknown`; inspect the exported clip and keep all provenance marks intact. Do not change `credit_source` from `free_daily` for this no-paid workflow.

## Review before spending more credits

- [ ] Pilot clip shows the intended subject and action throughout.
- [ ] It fits its narration beat and differs meaningfully from adjacent visuals.
- [ ] No generated text, UI, logo, statistic, endorsement, or factual detail could mislead viewers.
- [ ] Identity, scene, objects, motion, framing, and continuity are stable enough for the cut.
- [ ] Visible and invisible provenance marks are retained; this destination can accept the visible mark.
- [ ] Current Flow terms and rights for uploaded ingredients have been reviewed for the intended use.
- [ ] The exact prompt, model, clip length, free credits, watermark state, exported file, and metadata path are recorded.
