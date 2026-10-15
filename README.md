# Video Creation and Editing Skills

**Repository:** [github.com/pritoo733/video-creation-and-editing-skills](https://github.com/pritoo733/video-creation-and-editing-skills)

Reusable Codex skills for the full video lifecycle: research, concept development, scripting, asset preparation, video creation, editing, quality review, and delivery. They support personal stories, explainers, product demos, marketing pieces, social clips, events, footage recuts, motion graphics, and AI-assisted video.

## Skills

- [`creating-videos`](skills/creating-videos/SKILL.md) — take a video from idea through research, script, production, editing, review, and a finished export.
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
2. Research and script using [`research-and-script-ledger.md`](templates/research-and-script-ledger.md) when factual material needs sources.
3. Choose a creative mode, gather or create visuals, and plan scenes from [`scene-manifest.example.json`](templates/scene-manifest.example.json).
4. Keep project scripts, footage, generated assets, audio, timelines, and exports in the project folder. This repo contains no footage or account data.
5. Invoke `creating-videos` to carry the work through production, editing, review, and final delivery. Invoke `editing-videos` on its own when you already have a video and only need changes.

## Tooling and rights

The skills support source footage, photos, screen recordings, animation, generated video, voiceover, and mixed-media projects. Local Piper text-to-speech and FFmpeg are one optional workflow; editors and connected generation tools are also options when available. Confirm access, actual capabilities, pricing, and rights before relying on a tool. Never start a paid job, subscription, or trial without the user's explicit approval. Lessac `en_US-lessac-medium` was selected for the example project, but voice choice is configurable. Treat external processing, stock assets, music, and publishing as separate choices that require appropriate authorization.

## Repository scope

This repository provides workflow instructions and templates. It does not include the example video, transcript, footage, screenshots, voice models, or project-specific scripts. Clone it locally and add project assets in a separate working directory.
