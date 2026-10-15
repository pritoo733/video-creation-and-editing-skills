# Local Rendering Notes

Use these notes when a local render is appropriate. Confirm installed versions and actual input/output paths before writing commands. Keep generated audio, frame renders, subtitles, and intermediate scene clips in a working directory separate from source assets and final outputs.

## Piper narration

Piper can synthesize local narration when its runtime and selected voice model are available. Store the voice choice in project configuration rather than embedding it in scripts. Synthesize in sentence or scene units and record the model name, sample rate, synthesis settings, pronunciation substitutions, and audio duration for each unit. Preserve the selected model's license notice with the project.

Listen to an audition that includes the application's proper names, acronyms, numbers, and the intended speaking pace before generating the full narration. Do not infer gender identity, voice quality, or rights from a filename. Check model documentation and dataset terms for the specific voice release and intended distribution.

## FFmpeg assembly

For a landscape product tutorial, 1920×1080 at 24 or 30 fps is a practical master. Use H.264/yuv420p for broad playback compatibility and AAC audio when an MP4 delivery is requested. These are starting points, not mandatory platform guarantees. Confirm current destination specifications for uploads.

Use a scene manifest or editor timeline that records source asset, start/end, narration file, caption file, and overlays. Build caption timing from the final audio. Burn captions in only when requested or when the delivery context calls for it; otherwise provide an SRT sidecar. Add chapter metadata when the target player supports it.

Normalize narration consistently, retain headroom, and avoid clipping. If music is authorized, mix it quietly below speech and check the result on headphones and ordinary speakers. Fade only where it does not truncate a word.

Use deterministic intermediate filenames and log each render command and exit status. Resume completed scenes instead of silently replacing them. If a render fails, inspect the specific scene and its log, fix that cause, and rerender the affected scope. Validate the final joined export using [the review checklist](review-checklist.md).
