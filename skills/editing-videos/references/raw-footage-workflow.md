# Footage-first editing workflow

Use this route when the user supplies raw clips, interviews, a talking head, event coverage, or a partly edited timeline. The useful lesson from [browser-use/video-use](https://github.com/browser-use/video-use) is its staged process: inspect and transcribe source media, plan an edit decision list, render, then review every cut boundary. Its repository is MIT-licensed, but its documented default setup relies on ElevenLabs for transcription; this guide keeps the transferable workflow local and does not require that paid service.

## 1. Protect and inspect source media

- Keep originals read-only; create a project working copy and an explicit output folder.
- Inventory file names, duration, resolution, frame rate, rotation, audio channels, and codec. Identify duplicate takes and missing/corrupt media before editing.
- Review the footage and audio (or use a local transcript plus selective visual inspection) before proposing a story. Do not let the transcript alone decide which facial expressions, gestures, demonstrations, or emotional moments matter.
- Note each take's usable start/end, speaker, scene, action, technical issues, and story value in a source log.

## 2. Build an editable plan before destructive changes

Use a transcript with speaker labels and timestamps from an already installed local recognizer such as faster-whisper. Check proper names and technical vocabulary manually. Create a reversible edit decision list (EDL) with source in/out points, destination order, purpose, transition, dialogue/audio handling, caption text, and unresolved review notes. The timeline must preserve source identity and timing so the editor can reconstruct every cut.

For each cut, decide whether it should be a hard cut, J/L cut, short dissolve, or deliberate hold. Retain breaths and pauses that communicate meaning; remove dead air only when it helps. Use short audio fades only where needed to prevent clicks; do not force a single fade duration onto every scene. Color-correct shots to match each other before applying a look. Keep dialogue sync and room tone continuous when relevant.

## 3. Render a representative section first

Choose a passage with speech, movement, and at least one scene change. Render it using the actual target frame size, captions, audio chain, and transition plan. Review at normal speed, revise the recipe, then apply it to the full sequence. Do not treat an EDL, waveform, or contact sheet as evidence that the edit works.

## 4. Inspect every join and scene

After the full render:

1. Review the full timeline at normal speed with sound.
2. Check frames before, at, and after every cut and transition. Watch for black flashes, jumps, repeated frames, accidental truncation, uncovered words, abrupt room tone, mouth-sync shifts, or a mismatched color grade.
3. Listen at each join for clicks, pops, music jumps, abrupt ambience, and clipped consonants.
4. Check the final cut against the source log and EDL: every retained line/action is in the right order, any requested removals are complete, and no meaning or qualifications were lost.
5. Rebuild captions after dialogue or timing changes, then review caption sync and readability over actual footage.
6. Save source inventory, transcript, EDL/timeline, render settings, caption files, media rights, and final review notes beside the export.

Use [compose_video.py](../scripts/compose_video.py) for supported manifest-driven assembly when it fits the edit. Use a local non-linear editor when dialogue editing, J/L cuts, audio repair, color matching, or complex timing require more control. Check the installed tool and codec capabilities; never replace editorial judgment with automatic filler-word removal or a one-click grade.

## Free local transcription option

The repo's optional automatic workflow already installs faster-whisper locally for word timestamps. Use it only after checking model download size and machine capacity. For new installations, follow that workflow's `setup_free_tools.py`; do not add API keys or send user footage to external services without explicit authorization. A downloaded recognition model and any footage also have their own license/privacy considerations.
