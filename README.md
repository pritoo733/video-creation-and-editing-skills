# Video Creation and Editing Skills

Reusable Codex skills for planning, creating, editing, and reviewing many kinds of video: personal stories, explainers, product demos, marketing pieces, social clips, event videos, footage recuts, photo stories, motion graphics, and AI-assisted video.

## Skills

- [`creating-videos`](skills/creating-videos/SKILL.md) — develop a creative brief, script, storyboard, visuals, voice, and finished video from a concept or source material.
- [`editing-videos`](skills/editing-videos/SKILL.md) — revise, recut, caption, enhance, review, and export existing video while keeping edits reproducible.

## Install in Codex

Copy either skill folder into your Codex skills folder. On Windows PowerShell:

```powershell
$targetRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }
New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
Copy-Item -Recurse '.\skills\creating-videos' $targetRoot
Copy-Item -Recurse '.\skills\editing-videos' $targetRoot
```

For a repo-local or other agent runtime, copy the `skills` folders to that runtime's supported skills directory. Invoke a skill explicitly with `$creating-videos` or `$editing-videos`; automatic discovery can also use each skill's description.

## Start a project

1. Copy [`templates/production-brief.md`](templates/production-brief.md) into your project and describe its purpose, audience, tone, source material, destination, and rights.
2. Choose the creation mode and visual direction in [`creative-modes.md`](skills/creating-videos/references/creative-modes.md).
3. If the work uses scenes, create a scene manifest from [`scene-manifest.example.json`](templates/scene-manifest.example.json).
4. Keep project scripts, footage, generated assets, audio, timelines, and exports in that project's folder. This repo contains no footage or account data.
5. Use the creation skill to make the video and the editing skill for revisions or finishing.

## Tooling and rights

The skills support source footage, photos, screen recordings, animation, generated video, voiceover, and mixed-media projects. Local Piper text-to-speech and FFmpeg are one optional workflow; editors and connected generation tools are also options when available. Confirm access, actual capabilities, pricing, and rights before relying on a tool. Lessac `en_US-lessac-medium` was selected for the example project, but voice choice is configurable. Treat external processing, stock assets, music, paid services, and publishing as separate choices that require appropriate authorization.

## Repository scope

This repository provides workflow instructions and templates. It does not include the example video, transcript, footage, screenshots, voice models, or project-specific scripts. Clone it locally and add project assets in a separate working directory.
