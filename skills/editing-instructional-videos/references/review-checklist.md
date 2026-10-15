# Video Review Checklist

Review the final rendered export, not just the timeline or draft frames. Keep a short record of the method and findings.

## Content and continuity

- Check the opening, each chapter transition, every scene change, and the closing. Confirm that visuals support the narration and the sequence is understandable without hidden context.
- Inspect the first and last frames of every shot. Look for black frames, jumps, stale or mismatched captures, cursor obstruction, cropped controls, clipped graphics, and accidental blank space.
- Confirm that spoken claims match the source and on-screen state. Preserve qualifiers; do not convert examples, calculated scenarios, demos, or empty states into proof or promises.
- Verify that masking is complete and does not hide a control needed to understand the workflow.
- Confirm title cards, role labels, brand marks, and overlays remain consistent and inside safe margins.

## Narration and captions

- Listen to the opening, representative sections, scene joins, and final sentence. When possible, listen to the full export at normal speed. Describe sampling accurately if full listening was unavailable.
- Check names, acronyms, numbers, pauses, pace, tone, clipping, clicks, and room/noise artifacts. Generated speech may sound unnatural even when the words are correct.
- Compare captions against the final audio, including scene edits, pauses, line breaks, long reading times, overlaps, and final words. Recalculate timing after edits; do not reuse timestamps from replaced audio.
- Check speech loudness and peak level. Keep narration clear above any authorized music and avoid clipping; no music is required for instructional video.

## Technical export

Use FFprobe or an equivalent tool to inspect the deliverable. Confirm the container decodes end to end, expected video dimensions and frame rate, duration, audio stream and sample rate, subtitle sidecar or burned-in captions, and sensible file size. A successful metadata probe alone does not establish that the file plays correctly.

Example FFmpeg checks:

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of json final.mp4
ffmpeg -v error -xerror -i final.mp4 -f null -
```

If the full runtime is long, sample the opening and closing plus at least two frames per scene and additional frames around every edit. Generate contact sheets for human inspection. Inspect audio separately. Clearly distinguish frame sampling and decode checks from continuous playback.

## Repair and final record

Repair every material issue found and re-export. Review repaired scenes and run the relevant technical checks again. Record the final file name, runtime, dimensions, frame rate, audio format, caption format, review coverage, unresolved limitations, and source/edit manifest location. Do not label a partially reviewed render as fully reviewed.
