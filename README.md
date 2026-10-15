# Video Creation and Editing Agent Skills

**Repository:** [github.com/pritoo733/video-creation-and-editing-skills](https://github.com/pritoo733/video-creation-and-editing-skills)

Reusable, LLM-provider-neutral skills for the full video lifecycle: research, concept development, scripting, asset preparation, video creation, editing, quality review, and delivery. They support personal stories, explainers, product demos, marketing pieces, social clips, events, footage recuts, motion graphics, and AI-assisted video.

The skills follow the open [Agent Skills format](https://agentskills.io/specification): a folder with a `SKILL.md` file and optional references or templates. They work directly in agent products that load this format. Other LLM setups can use them by adding the relevant `SKILL.md` and referenced files to the model's instructions/context. The skills do not depend on a specific model provider; access to browsing, editing, voice, and video-generation tools depends on the host environment.

## Skills

- [`creating-videos`](skills/creating-videos/SKILL.md) — take a video from idea through research, script, production, editing, review, and a finished export.
- [`editing-videos`](skills/editing-videos/SKILL.md) — revise, recut, caption, enhance, review, and export existing video while keeping edits reproducible.

## Install in an agent

Copy either skill folder into the skills directory scanned by your LLM agent. Keep each folder's references alongside its `SKILL.md`. For example, on Windows PowerShell:

```powershell
$agentSkillsDirectory = 'SET_TO_YOUR_AGENT_SKILLS_DIRECTORY'
New-Item -ItemType Directory -Force -Path $agentSkillsDirectory | Out-Null
Copy-Item -Recurse '.\skills\creating-videos' $agentSkillsDirectory
Copy-Item -Recurse '.\skills\editing-videos' $agentSkillsDirectory
```

If your agent has no skill loader, include the desired `SKILL.md` and its linked references in the task context. Use the invocation method supported by your agent, or ask for the video workflow in plain language.

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
