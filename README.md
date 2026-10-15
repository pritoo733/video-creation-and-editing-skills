# Video Production Skills

Reusable Codex skills for creating and editing instructional product videos. The workflow is based on a completed, long-form product walkthrough assembled from genuine demo captures, Piper narration, timed captions, and FFmpeg renders.

## Skills

- [`creating-instructional-videos`](skills/creating-instructional-videos/SKILL.md) — plan and produce a narrated product or software walkthrough from an authorized app session and approved source material.
- [`editing-instructional-videos`](skills/editing-instructional-videos/SKILL.md) — revise, caption, re-render, inspect, and deliver an existing video while keeping edits reproducible.

## Install in Codex

Copy either skill folder into your Codex skills folder. On Windows PowerShell:

```powershell
$targetRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }
New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
Copy-Item -Recurse '.\skills\creating-instructional-videos' $targetRoot
Copy-Item -Recurse '.\skills\editing-instructional-videos' $targetRoot
```

For a repo-local or other agent runtime, copy the `skills` folders to that runtime's supported skills directory. Invoke a skill explicitly with `$creating-instructional-videos` or `$editing-instructional-videos`; automatic discovery can also use each skill's description.

## Start a production

1. Copy [`templates/production-brief.md`](templates/production-brief.md) into a project folder and fill in the audience, purpose, roles, platform, length, voice, and output requirements.
2. Capture only approved, representative app states and create a scene manifest based on [`templates/scene-manifest.example.json`](templates/scene-manifest.example.json).
3. Keep project scripts, captures, audio, timelines, and exports in that project folder. This repo contains no client/demo footage or account data.
4. Follow the creation skill for scripting, voice auditions, scene assembly, captions, export, and review. Use the editing skill for later revisions.

## Tooling and rights

The reference workflow uses local Piper text-to-speech and FFmpeg, with image tools for simple title cards and callouts. Other local or connected tools are optional. Confirm each tool is installed and usable; the skill does not install software or grant provider access. The Lessac `en_US-lessac-medium` voice was selected for the example project, but voice choice is configurable. Check the exact model and dataset license for the intended distribution before production. Treat external generation, stock assets, music, paid services, and publishing as separate choices that require the relevant authorization.

## Repository scope

This repository provides workflow instructions and templates. It does not include the Three Eagles video, transcript, screenshots, Piper model files, or project scripts. Clone it locally and add project assets in a separate working directory.
