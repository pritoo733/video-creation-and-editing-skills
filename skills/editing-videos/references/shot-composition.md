# Local shot composition

Use `python scripts/compose_video.py timeline.json final.mp4 --ffmpeg /path/to/ffmpeg` from this skill directory, or invoke the script by its absolute path. It requires Python 3 and an installed FFmpeg build with libx264; caption burning also requires the subtitles/libass filter. No hosted API or Python media package is required. Do not download or install dependencies without the authorization applicable to the environment.

The renderer is an optional execution route for a planned edit, not an automatic director, footage search service, or editor replacement. It accepts local video/image shots, source trims, aspect-specific focal points, optional still-image camera moves, timed PNG/image overlays with fades and eased vertical entrances, hard cuts and selected FFmpeg transitions, final mixed audio, and ASS/SRT captions. Use a full editor or a custom compositor for tracking, rotoscoping, speed ramps, complex masks, advanced 3D, or synchronized dialogue editing.

## Manifest

Paths are resolved relative to the manifest. Keep all clips local and preserve originals. `duration` is the full source interval including any transition handle. The next shot's transition overlaps its beginning with the previous shot, so final runtime is the sum of shot durations minus overlap durations. Use durations on the output frame grid.

For a narrated montage, give every shot a globally unique `visual_id`, a `beat_id` for the sentence or phrase it serves, a `source_id` identifying its full-frame source, a concise `visual_action`, and a `why_it_fits` tied to the exact words. These are editorial metadata; they do not prove relevance automatically. Run `python scripts/audit_visual_sequence.py timeline.json` before rendering. The audit rejects missing descriptions, duplicate visual IDs, repeated adjacent source IDs, repeated screenshots, and long spoken beats represented by only one shot. Read its findings and inspect the source frames: two clips can look alike even when their filenames differ.

```json
{
  "format": {"width": 1080, "height": 1920, "fps": 30},
  "expected_duration": 6.8,
  "audio": "audio/final-mix.wav",
  "captions": "captions.ass",
  "shots": [
    {
      "path": "footage/owned-camera-shot.mp4",
      "type": "video",
      "kind": "owned",
      "in": 2,
      "duration": 3.5,
      "focus_x": 0.55,
      "purpose": "Show the camera action that supports the opening promise",
      "visual_id": "camera-wide-setup-01",
      "beat_id": "opening-idea",
      "source_id": "camera-setup-wide",
      "visual_action": "The camera is assembled on the tripod",
      "why_it_fits": "The narration introduces an idea becoming a filmed video",
      "overlays": [
        {"path": "graphics/short-label.png", "x": 70, "y": 200, "width": 850, "start": 0.2, "end": 2.8, "fade": 0.2, "slide_y": 24}
      ]
    },
    {
      "path": "footage/owned-editor-shot.mp4",
      "type": "video",
      "duration": 3.5,
      "purpose": "Connect production to the editor's next action",
      "transition": {"type": "fade", "duration": 0.2}
    }
  ]
}
```

`fit` defaults to `cover`; `contain` retains the whole frame with padding. `focus_x`/`focus_y` range from zero to one. Image shots may use `motion: {"zoom_start": 1.0, "zoom_end": 1.08}` for a purposeful push. This is a still-image move, not evidence of native footage. Overlays use the manifest's pixel coordinates; `--scale 0.5` scales the canvas and overlay geometry for a preview. Review the final-size export separately.

For `kind: "stock"`, add a `rights` object containing `source_url`, `license_url`, `checked_on`, `evidence` (a saved local evidence file), `status: "reviewed"`, and `intended_use`. The renderer checks record completeness; an operator must actually verify the terms and chosen use. It does not establish rights from a URL or flag.

## Execution and review

Use `--validate-only` to check the timeline and local references. `--workdir` selects the project cache/log directory. Normalized shots are cached using their configuration and source/overlay metadata. Failed shots remain pending and are not reused as successful cache entries. Inputs shorter than requested fail rather than silently looping or holding their last frame. Keep the returned `.edit.json` with the project for source intervals, shot purposes, and output timings.

Make a short pilot manifest containing actual consecutive shots. Watch or sample it before committing to the entire treatment. Decode and review the final joined export; an execution success is not a creative approval. The renderer uses a supplied final audio mix, pads silence if it is short, and applies a general loudness starting point. Verify complete speech, music balance, destination requirements, and final loudness independently. It does not rewrite scripts or regenerate caption timestamps.

Use two or more distinct, directly related visuals during a narrated sentence that lasts around four seconds or longer when the story can support the change. Avoid holding one B-roll clip behind several changing interface screenshots. For promos, a 1.5–3-second shot interval is a starting point; adapt to action and reading time. Never make frame-by-frame flashes. Let tutorials and detailed disclosures stay up long enough to read.

For a sampled motion diagnostic, run `python scripts/motion_diagnostics.py final.mp4 --ffmpeg /path/to/ffmpeg --output motion.json`. It measures changes in a central content region, excluding most title/footer regions. Report the ROI, sampling interval, and near-static findings. Noise, pans, and visual effects can inflate movement; quiet footage or a diagram may appropriately remain still. This is a way to find passages to inspect, not a professional-quality score or an automatic approval gate.
