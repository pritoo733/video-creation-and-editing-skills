# Video Creation and Editing Agent Skills

**Repository:** [github.com/pritoo733/video-creation-and-editing-skills](https://github.com/pritoo733/video-creation-and-editing-skills)

Reusable, LLM-provider-neutral skills for the full video lifecycle: research, concept development, scripting, asset preparation, video creation, editing, quality review, and delivery. They support personal stories, explainers, product demos, marketing pieces, social clips, events, footage recuts, motion graphics, and AI-assisted video.

The skills follow the open [Agent Skills format](https://agentskills.io/specification): a folder with a `SKILL.md` file and optional references or templates. They work directly in agent products that load this format. Other LLM setups can use them by adding the relevant `SKILL.md` and referenced files to the model's instructions/context. The skills do not depend on a specific model provider; access to browsing, editing, voice, and video-generation tools depends on the host environment.

The workflow emphasizes evidence-backed scripts, motion planned around story beats, reference-video analysis, source-grounded recaps and dubs, an early representative sample, and a coverage-based review of the export. It was informed by [awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills), [lanshu-create-ai-presenter-video](https://github.com/cclank/lanshu-create-ai-presenter-video), [video-production-skills](https://github.com/Pluviobyte/video-production-skills), [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft), [Violin](https://github.com/shang-zhu/violin), [video-recap-skills](https://github.com/zenstory-ai/video-recap-skills), [Recordly](https://github.com/webadderallorg/Recordly), [chatgpt-video-editing-skills](https://github.com/Jaycheng1103/chatgpt-video-editing-skills), [chengfeng-videocut-skills](https://github.com/Agentchengfeng/chengfeng-videocut-skills), [jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill), [OpenMontage](https://github.com/calesthio/OpenMontage), [OpenCreator](https://github.com/krillinai/OpenCreator), [remotion-video-skill](https://github.com/wshuyi/remotion-video-skill), and [video-editing-skill](https://github.com/maxazure/video-editing-skill). This repository adopts transferable workflow ideas without requiring any listed provider, editor, or toolkit.

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
3. Choose a creative mode, write a visual treatment, gather or create visuals, and plan scenes from [`scene-manifest.example.json`](templates/scene-manifest.example.json). For motion-led work, use the [visual beat sheet](templates/visual-beat-sheet.md) and save successful patterns with the [shot recipe](templates/shot-recipe.md). For a supplied reference, recap, or dub, load the [reference-video](skills/creating-videos/references/reference-video-analysis.md) or [source-based video guide](skills/creating-videos/references/source-based-video.md). For presenter or talking-head videos, follow the optional [presenter workflow](skills/creating-videos/references/presenter-workflow.md). For multi-step videos, copy the [`coverage matrix`](templates/coverage-matrix.md) to track every required point through final review.
4. Keep project scripts, footage, generated assets, audio, timelines, and exports in the project folder. This repo contains no footage or account data.
5. Invoke `creating-videos` to carry the work through production, editing, review, and final delivery. Invoke `editing-videos` on its own when you already have a video and only need changes.

## Tooling and rights

The skills support source footage, photos, screen recordings, animation, generated video, voiceover, and mixed-media projects. Local Piper text-to-speech and FFmpeg are one optional workflow; editors and connected generation tools are also options when available. Confirm access, actual capabilities, pricing, and rights before relying on a tool. Never start a paid job, subscription, or trial without the user's explicit approval. Lessac `en_US-lessac-medium` was selected for the example project, but voice choice is configurable. Treat external processing, stock assets, music, and publishing as separate choices that require appropriate authorization.

## Repository scope

This repository provides workflow instructions and templates. It does not include the example video, transcript, footage, screenshots, voice models, or project-specific scripts. Clone it locally and add project assets in a separate working directory.
