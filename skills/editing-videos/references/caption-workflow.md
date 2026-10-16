# Accurate, readable captions

Use captions as editorial text, not decoration. This process is inspired by the local, word-level correction and preview workflows in [FreeCap](https://github.com/giladbas/FreeCap) and [Capite](https://github.com/muneebkhan08/Capite). Their repositories describe MIT licensing and local Whisper/faster-whisper transcription; check the upstream code, dependency, and model terms before installing or bundling either project. This skill does not require either app.

## Workflow

1. **Transcribe the final dialogue.** Use the final narration or a local speech recognizer. If a transcript already exists, compare it against the finished audio rather than trusting it after edits.
2. **Correct the words.** Review speaker names, product terms, acronyms, numbers, contractions, punctuation, disfluencies, and context-dependent terms. Keep a private list of approved spellings for repeated work.
3. **Regroup word timing into readable cues.** Keep meaning together; use short phrases instead of one-word flashing captions. Set line length and reading rate for the platform and language. Avoid splitting a name or phrase across a cut without a reason.
4. **Preview on actual picture.** A local word-level editor such as FreeCap or Capite can help correct phrase grouping and timing; a subtitle editor such as Aegisub can edit ASS styling. Use a local install and inspect current license/requirements. Check captions over bright, dark, busy, and interface shots.
5. **Choose a style for this format.** Use a clean, stable phrase style for interviews, documentaries, instruction, or emotionally quiet work. For energetic short-form or a lively explainer, a restrained word-follow highlight and small phrase entrance can add energy. Keep a strong outline/shadow or a quiet plate for contrast, use the project's accent color consistently, and keep captions inside safe areas. Avoid large bounces, flashing words, emoji clutter, all-caps blocks, and captions that obscure faces, controls, or evidence.
6. **Export both deliverables where useful.** Keep a platform-ready burned-in version and an editable sidecar (SRT/VTT/ASS) when requested or useful. Preserve the caption source and its connection to final audio timing.
7. **Recheck after every final edit.** Play representative passages and review every timing-sensitive join. Confirm the first and last spoken words, sync after pauses, and sync after transitions. Run caption parsing/technical checks if installed; then watch the final render.

## Quality gate

- Verbatim accuracy for the actual final words, including names and numbers.
- Captions appear and disappear on time and do not overlap unintentionally.
- Pacing is comfortable, lines break by phrase, and cue duration supports reading.
- Contrast and size remain sufficient at the target playback size and against varied footage.
- Captions do not block essential UI labels, faces, disclosures, or other required content.
- Sidecar and burned-in caption text match, unless the deliverable explicitly needs different versions.
- Language, accessibility, and platform-specific requirements are reviewed for the actual audience.

## Automatic-free renderer styles

The no-paid-tools automatic renderer writes both a plain SRT sidecar and an editable ASS subtitle file. `caption_style` defaults to `kinetic`: the ASS captions use recognized or estimated word timing for a left-to-right accent-color highlight and a subtle phrase entrance. The accent uses `palette.accent` when provided. Set `"caption_style": "clean"` in the plan for stable phrase captions with a light fade and no animated word highlight. Choose based on tone and audience; the animated style is not appropriate for every video. ASS supports timed karaoke highlights and animated transforms ([Aegisub tag reference](https://aegisub.org/docs/latest/ass_tags/)); FFmpeg renders ASS through its subtitles filter when built with libass ([FFmpeg subtitles filter](https://www.ffmpeg.org/doxygen/trunk/vf__subtitles_8c.html)). Review the ASS render over the actual footage at phone size and provide/retain the SRT for accessible player-controlled captions where the platform supports it.

Example plan setting:

```json
{
  "caption_style": "kinetic",
  "palette": {"accent": "#41DDBF"}
}
```
