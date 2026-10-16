# Automatic video production with free local tools

Use this route when the user has an idea, topic, or brief but no footage, and has asked for a workflow with no paid services. The agent still does the creative work: research, concept, script, shot plan, source queries, and visual review. The local runner assembles that plan. It does not make every creative decision well by itself, and no workflow can promise “best” results for every topic.

For a brief asking for polished, custom motion graphics, start with [motion-design production](motion-design-production.md) instead. It provides an original editable HTML study and a local frame renderer for connected animation. This montage/diagram runner remains useful when its available source footage and four graphic forms suit the story; a free-only budget does not require choosing those simpler layouts.

## What this route can make

- Search Wikimedia Commons for relevant video clips through its public API without an API key. Automatically select only files whose metadata matches a conservative public-domain or CC BY allowlist, retain the source and license evidence, and create attribution credits. NC, ND, SA, unknown terms, missing attribution, and stated extra restrictions are excluded.
- Create original moving process diagrams, sourced charts, cycles, and comparisons locally. These are useful when stock footage would be decorative or misleading.
- The built-in graphic renderer supports four deterministic, scene-timed layouts: process, sourced chart, cycle, and two-sided comparison. For custom HTML/SVG/React motion, use the optional [Motion library workflow](motion-library-workflow.md) with a frame-seekable local renderer; the Motion package is not a dependency of `auto_produce.py`.
- Synthesize local English narration with Pocket TTS on CPU by default, or choose Piper with `--tts-engine piper`. The default preset is `bill_boerst`, a CC0 Voice-Zero reference sample; it is the best candidate in Pocket's bundled English catalog for a male North American read, but the upstream Pocket catalog does not certify accent or gender, so audition it before use. Pocket TTS requires its package and downloads model weights on first use. The model repo is gated: users must review and accept its access terms on Hugging Face (which requests contact-information sharing) and authenticate before weights can download. The model weights are CC BY 4.0; each voice has separate dataset terms, recorded by setup in `runtime.json` and copied into `CREDITS.md`. Select only a voice whose terms fit the distribution; `cosette` and `jean` are noncommercial-only. The `alba` preset is CC BY 4.0 and should be attributed. TTS package and model generation are free; the first package/model download needs internet and disk space.
- Create exact-script captions, compare them with local Whisper transcription, and use recognized word timestamps when they agree. If speech differs, flag the mismatch and preserve the script captions for review.
- Mix narration and optional music/effects/ambience tracks. The mixer ducks music under speech and writes an editable track manifest. The example plan does not add a synthetic sine-wave “score”; silence is preferable when no suitable cue exists.
- Generate an optional original local score with [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) in a separate environment after confirming the current model/license terms, hardware, and disk needs. This is not part of the lightweight runner or default install; if the model cannot run, use a rights-cleared source cue or no music.
- To include a locally generated or licensed score, add a `music` object to `plan.json`. `path` is relative to the plan file; the remaining rights fields are copied into the project manifest and `CREDITS.md`. The runner copies the music into the project output and ducks it under narration:

```json
"music": {
  "path": "assets/score.wav",
  "gain_db": -22,
  "rights": {
    "creator": "ACE-Step 1.5 (local generation)",
    "source_url": "https://github.com/ace-step/ACE-Step-1.5",
    "license": "Verify the exact model-card terms used for this output",
    "license_url": "https://huggingface.co/ACE-Step/Ace-Step1.5",
    "checked_on": "YYYY-MM-DD",
    "attribution": "Prompt and generation settings are recorded in project notes."
  }
}
```

Use the current exact model and output terms; do not copy this example's placeholder license wording as proof. `music: null` produces no music. The legacy `original-ambient` option makes a quiet harmonic texture, not a professionally composed soundtrack.
- Export MP4, SRT/ASS captions, credits, a contact sheet, candidate selection log, audio manifest, JSON edit manifest, and an OpenTimelineIO timeline.

It does not use a hosted video-generation API, paid stock account, or paid TTS service. It cannot manufacture documentary evidence, product UI, testimonials, or genuine camera footage. Original diagrams are illustrative. Online source search and the initial Whisper model download require internet access; rendering and speech are local. The first model downloads use disk space and CPU time. Results depend on suitable public media being available, hardware, research quality, and human review. No API cost does not mean that each asset has no obligations: distribute required CC BY credit and check privacy, trademark, property, and other rights that the file license does not clear.

This route adapts useful production ideas from [OpenMontage](https://github.com/calesthio/OpenMontage)—a planned pipeline, inspectable scene board, and auditable run record—to a no-paid-service setup. It does not copy OpenMontage source code, call its provider integrations, or require its React/Remotion, cloud, or API-key paths. OpenMontage documents its zero-key stock/open-archive route separately from examples that use paid generation; this workflow stays on local tools and allowlisted free media.

## Install once

From the repository root, Python 3.10 or later is required. Windows PowerShell:

```powershell
python skills/creating-videos/scripts/setup_free_tools.py --dest .video-tools --tts-engine pocket --pocket-voice bill_boerst
python skills/creating-videos/scripts/doctor_free_tools.py .video-tools/runtime.json
```

Accept the model access conditions at <https://huggingface.co/kyutai/pocket-tts>, then authenticate with `hf auth login` before the first render if the weights are gated for your account. Rendering uses the selected model locally on CPU. Use `--pocket-voice` to choose another supported English preset; check its license in the linked voice catalog before distributing, especially for commercial work. The setup step records the selected voice's source, license, and attribution in `runtime.json`; preserve the generated output's `CREDITS.md`. Use `--tts-engine piper` if you prefer the existing ungated Piper workflow or Pocket model access/resources are unsuitable.

macOS/Linux:

```sh
python3 skills/creating-videos/scripts/setup_free_tools.py --dest .video-tools --tts-engine pocket --pocket-voice bill_boerst
python3 skills/creating-videos/scripts/doctor_free_tools.py .video-tools/runtime.json
```

Setup creates a local virtual environment and fetches the listed open-source packages; Piper also downloads the approved voice model. FFmpeg is supplied by `imageio-ffmpeg`. Piper requires no account or API key; Pocket TTS model access requires a Hugging Face account, accepting the model terms, and authentication. Review package and model licenses for the planned use. `doctor_free_tools.py` checks imports, required voice files, FFmpeg filters, and Python dependency health without making a video.

## Create from an idea, not from user footage

Tell the LLM: “Create a video about [topic] for [audience], [purpose], [length and format], with no supplied footage. Use only free tools and appropriately licensed media. Research factual claims, write and revise the narration, build a varied shot plan, run the automatic-free workflow, inspect the contact sheet and captions, fix mismatches, and report any unavailable visual.” Do not ask the user to write JSON. The LLM should turn the approved brief into `plan.json`, using the example as a schema reference. Confirm any unresolved factual claims before rendering.

Copy [`../../../examples/automatic-free/plan.json`](../../../examples/automatic-free/plan.json) and replace its sample subject, narration, source-backed claims, and shot choices. Each narration beat contains one to four short visual actions. Each visual must explain why it supports that exact spoken line. Choose a graphic form that explains the content: `process` for ordered steps, `cycle` for a repeating loop (optionally name its `center_label`), `comparison` for two clearly labeled states (with two short `details` strings), or `chart` for sourced numeric data. A chart requires checked values and a source. Match shot duration to the spoken beat. Add `source_in` only when a reviewed clip interval needs a deliberate trim. Use a stock query specific to visible content, not broad mood terms. An empty search or insufficient clip duration is a sourcing gap: revise the query, use a truthful original graphic, or tell the user; do not silently substitute unrelated media.

For an explicit visual checkpoint, collect assets and build the board first:

```powershell
.\.video-tools\Scripts\python.exe skills\creating-videos\scripts\auto_produce.py path\to\plan.json --output path\to\project\output --runtime .video-tools\runtime.json --draft-only
```

Open `storyboard.html`. It pairs each shot preview with the exact narration beat, the reason for the choice, and the source/license links. If a visual is weak, revise the plan and regenerate the board. After review, run the regular command below to render. This checkpoint is optional; omit `--draft-only` when you want the workflow to continue through final rendering automatically.

Run from the repository root:

```powershell
.\.video-tools\Scripts\python.exe skills\creating-videos\scripts\auto_produce.py path\to\plan.json --output path\to\project\output --runtime .video-tools\runtime.json
```

```sh
.video-tools/bin/python skills/creating-videos/scripts/auto_produce.py path/to/plan.json --output path/to/project/output --runtime .video-tools/runtime.json
```

Keep the output beside the project rather than committing generated source media or model weights to this skills repository. Do not use a symlink or URL as a substitute for inspecting the actual asset.

## Review and repair

The renderer validates timing and decodability, but software checks cannot judge whether a shot tells the story. Review these outputs before calling a video finished:

1. Play the full MP4 with sound. Check that narration is natural and intelligible, transitions have no gaps, the mix does not clip, and the ending lands.
2. Inspect `review-contact-sheet.jpg` and every saved `*-preview.jpg`. Reject unrelated visuals, misleading context, repeated compositions, logos/people that imply an endorsement, or footage that does not visibly match its description. Inspect important footage at several points, not only its midpoint.
3. Read the shot manifest and `candidate-log.json`. Verify every source interval, distinct source, narration-specific purpose, and license page. A metadata allowlist is not a legal clearance.
4. Play the captions and compare `transcript.json` with narration. When local speech recognition disagrees, the renderer now preserves matching word timings and estimates only the mismatched spans; the method and affected word indexes are recorded for review. Correct these captions before delivery. Check cue timing, line breaks, contrast, safe areas, and readability on a phone.
5. Review `CREDITS.md`; retain required CC BY attribution when sharing. Keep source licenses, media, manifests, timeline, and output together for an editable handoff.
6. If any required claim/source/shot is unresolved, return to research or planning. Render a corrected cut and review the new export, not only its plan.

`review.json` records validation status, stream properties, caption comparison, source-ratio, warnings, and a pending creative-review field. Leave it pending until the above review is performed; a successful encode does not establish editorial, factual, accessibility, or legal quality.

## Inputs and outputs

Plan schema and a worked sample: [`../../../examples/automatic-free/plan.json`](../../../examples/automatic-free/plan.json). The output is a project folder containing `final.mp4`, `editable.otio`, `timeline.json`, `audio-tracks.json`, `captions.srt`, `captions.ass`, `transcript.json`, `CREDITS.md`, `storyboard.html`, `storyboard.json`, `production-log.json`, `review-contact-sheet.jpg`, `candidate-log.json`, and local working sources/evidence. The log records production stages and failures. Treat the edit manifest and separate audio sources as the practical editable source of truth; OTIO notes that caption rendering and mix automation need reconstruction in an external editor.

For higher control or non-English work, keep this workflow's evidence, narration, and timing checks, then use a compatible local editor or other free tools. Check current tool licensing and hardware demands before installing optional systems. Paid hosted generation is outside this route.
