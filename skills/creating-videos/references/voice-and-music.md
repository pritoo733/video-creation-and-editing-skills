# Voice and music: local, rights-aware workflow

Use this guide when a project needs narration, voice replacement, voice matching, background music, or a deliberate audio arc. Separate the license for the software from the license on the model weights, dataset, voice, and generated result. “Open source,” “free to download,” and “free for commercial use” are different claims.

## Choose the route before generating

1. Confirm purpose and distribution: private/noncommercial, internal, monetized, or commercial client work.
2. Prefer an approved human recording or a properly licensed, local TTS voice when natural performance is adequate.
3. For local text-to-music, evaluate [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5). Its upstream project and model card state MIT licensing and commercial use of generated music. This is an optional install, not a dependency of this repository. Check the model page and project license again at use time, because terms can change. It needs Python 3.11–3.12; CUDA is recommended, while MPS, ROCm, Intel XPU, and CPU are listed alternatives. Consumer hardware can run some variants, but slower devices may take much longer. Generate to the project folder, not this skills repository.
4. For voice cloning, evaluate [OmniVoice](https://github.com/k2-fsa/OmniVoice) only when the project is noncommercial and its exact current terms permit the planned distribution. The source code is Apache-2.0, but the official pretrained model card says the weights are CC BY-NC due to training data. Do not use those weights for commercial videos, monetized publication, or client deliverables. Voice cloning is not audio editing: it synthesizes new speech from text and an audio reference.
5. Never clone a real person's voice without documented permission covering synthetic speech and intended use. Do not imitate a public figure, create deceptive impersonations, or upload private reference speech without authorization. Keep reference audio and saved voice prompts private; do not commit them.

## Optional local music generation with ACE-Step

Install and run ACE-Step from its official project instructions in a separate environment. Do not install its large model stack into the lightweight automatic-free environment. Confirm GPU/runtime compatibility and disk space first. Keep prompts original; describe musical properties rather than naming a living artist or asking for a near-copy of a protected song.

Build the prompt from the video treatment:

```text
Instrumental background score for a [duration]-second [video purpose] aimed at [audience].
Emotional arc: [opening feeling] -> [development] -> [ending feeling].
Tempo/energy: [range and movement]. Palette: [specific instruments/textures].
Leave clear frequency and rhythmic space for spoken narration. No vocals, no lyrics,
no recognizable melody, no sudden hits under speech. End with a clean resolved tail.
```

Generate several alternatives, then audition them against the actual narration and edits. Select for story fit, not prompt match alone. Check that transitions, key changes, and percussion do not fight cuts or consonants. Edit the selected cue to picture, fade it intentionally, duck it beneath speech, and render from a lossless or high-quality source. Record model/revision, prompt, generation settings, file hash, and license evidence in the project's asset ledger. Listen to the mix on headphones and ordinary speakers; measure loudness/true peak for the named delivery platform when relevant.

If ACE-Step cannot run on the available hardware, use a suitable track from an explicitly licensed source such as Wikimedia Commons or an original score created with locally installed audio tools. Save the exact source page, creator, license/version, required attribution, download date, and any modifications. Exclude unknown, NC, ND, or incompatible terms for commercial work. Silence is better than an unlicensed or distracting cue.

## Voice cloning / synthesis checklist

- Confirm the exact model-weight license separately from the source-code license and voice-reference rights.
- Pocket TTS is an optional local English TTS route for the automatic-free workflow. The upstream source code is MIT and its published model weights are CC BY 4.0, but the model repository currently gates download behind access terms and requests contact-information sharing. Review those terms and decide whether to accept them before setup. Voice recordings have separate licenses: consult the [official voice catalog](https://huggingface.co/kyutai/tts-voices), retain any required attribution, and avoid Expresso/EARS-derived English presets (`cosette`, `jean`) for commercial work because their source datasets are CC BY-NC 4.0. The repo defaults to `bill_boerst`, a CC0 Voice-Zero reference. It is the strongest bundled candidate for a male North American read, though Pocket's own catalog does not publish gender/accent labels, so audition the generated sample before treating that as confirmed. Kyutai's `alba` preset uses Alba MacKenna recordings under CC BY 4.0; attribute the voice and link its source. The `michael` preset comes from VCTK under CC BY 4.0. Setup with `setup_free_tools.py --tts-engine pocket --pocket-voice bill_boerst`; first use downloads model weights, and synthesis then runs locally on CPU. Hardware and voice selection affect speed and sound, so audition the complete narration before use.
- For Pocket TTS, include Kyutai model-weight attribution and the selected voice's source/license attribution in the project credits; do not infer voice terms from the package or model license. A voice choice is not a guarantee of a particular national accent.
- For OmniVoice, label its default pretrained weights **noncommercial only**. A license for OmniVoice's Python package does not change that model-weight restriction.
- Use a clean, consented reference clip and accurate transcript; follow upstream recommendations and do a pronunciation/pacing audition before generating the full script.
- Break narration into natural sections. Direct breathing, emphasis, and pause structure through the script; do not rely on post-processing to make an unsuitable performance sound human.
- Normalize names, acronyms, and numbers; audition difficult names, transitions, and the final line.
- Avoid extreme pitch shifting or time stretching. Use gentle EQ, de-noising, compression, and room tone only when they improve intelligibility without artifacts.
- Compare the final voice against the approved script and re-transcribe after edits. Retain the generated waveform and editable project files alongside the final render.
- Disclose synthetic speech when the audience, contract, policy, or law requires it. Never imply an unconsented person endorsed the message.

## Do not confuse these licenses

| Component | What to verify |
| --- | --- |
| Repository code | Source-code license and notice requirements |
| Downloaded model weights | Model-card license and any field-of-use restrictions |
| Voice reference | Speaker consent, recording rights, and scope of permission |
| Generated music/audio | Model terms, similarity risk, output rights, and project-specific restrictions |
| Stock/library music | Exact asset license, attribution, and any platform/distribution conditions |

Model and asset terms change; recheck the canonical license pages before release and keep evidence with the project.
