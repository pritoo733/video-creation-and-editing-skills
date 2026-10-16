# Local motion-design route: validation record

Checked on 2026-10-16. This validates a new reusable composition route, not a claim that a particular model always produces excellent films.

## What changed

The previous automatic-free route offered public footage and four diagram forms. Rich HTML animation was documented as an optional external route. A brief asking for custom motion design now leads to [motion-design production](../../skills/creating-videos/references/motion-design-production.md), with an executable local HTML renderer and an original editable study. Its composition is authored for each project rather than selected from a fixed set of title-card layouts.

The study demonstrates a contour changing role across four beats, line-level masked type, staged path drawing, an original layered illustration, and a closing mark. It has separate landscape and portrait placement. It contains no product claims, external footage, bundled third-party fonts, paid API calls, or copied showcase artwork. It is a technique study, not a finished promotional film.

## Observed checks

| Check | Result |
|---|---|
| Full landscape encode | 12 seconds, 1280 × 720, 30 fps, 360 frames, H.264 MP4 |
| Full FFmpeg decode of the encoded pilot | Passed |
| Landscape scene/handoff snapshots | 22 sampled frames; reverse seeks produced identical PNG hashes |
| Portrait layout | 1080 × 1920, 22 snapshots; reverse seeks produced identical PNG hashes; portrait MP4 not encoded |
| Visual inspection | Scene and transition contact sheets plus a full-size portrait frame inspected; diagram labels enlarged after review |
| Renderer integration checks | Four passed: seek consistency and fps cue mapping; stateful animation rejected; remote asset blocked; missing encoder failed without a finished export |
| Skill installation | Passed with renderer, HTML study, and rewritten shared-template link available outside the checkout |
| Existing repository checks | All 31 distinct tests passed across the suite run and the follow-up of six FFmpeg-dependent checks |
| Skill frontmatter/scaffold validation | Passed |

The initial test discovery ran 25 checks successfully and skipped six because `FFMPEG_BIN` was unset. Those six were then run with the installed local FFmpeg and all passed. Runtime: Node 22.18.0, Playwright 1.54.2, Chromium 139.0.7258.5, FFmpeg 7.1.

## Reproduce

Install Playwright/Chromium in the video project and provide a local FFmpeg path, as described in the guide. From the repository root:

```sh
node skills/creating-videos/scripts/render_motion.cjs skills/creating-videos/assets/motion-starter/index.html --output renders/motion-study.mp4 --ffmpeg /path/to/ffmpeg
node skills/creating-videos/scripts/render_motion.cjs skills/creating-videos/assets/motion-starter/index.html --output renders/motion-study-portrait.mp4 --width 1080 --height 1920 --stills-only
python -m unittest discover -s tests -p test_motion_render.py -v
```

The renderer writes snapshots and a technical review JSON beside each output. Generated videos and review frames stay outside committed source. Use another output name for a revision or explicitly pass `--overwrite`.

## Limits of this validation

The pilot has no audio; this pass did not assess a finished voice/music mix. Sampled frame inspection and a successful decode do not establish the continuous film's artistic merit. The renderer leaves creative review pending. A deliverable still needs a complete normal-speed review with its final sound, captions, real source claims, and destination-specific readability checks. Browser/font differences across machines can change typography; rerender and inspect on the actual production host.
