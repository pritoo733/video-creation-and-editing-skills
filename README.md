# Video Creation & Editing Skills

![A video team moving from research and storyboards through editing to a reviewed final cut](assets/video-workflow-hero.png)

Create a video from an idea, or improve footage you already have. These reusable skills guide any LLM that supports the open [Agent Skills format](https://agentskills.io/specification) through planning, production, editing, and review.

**Research · Script · Visuals · Edit · Captions · Sound · Review**

[Get started](#get-started) · [Create a video](skills/creating-videos/SKILL.md) · [Edit a video](skills/editing-videos/SKILL.md)

## Choose a skill

### Create a video

For new videos: research, scripts, storyboards, footage, motion graphics, narration, editing, and final review.

[Open the creating-videos skill](skills/creating-videos/SKILL.md)

### Edit a video

For existing footage: review, recut, captions, sound, motion, export, and quality checks.

[Open the editing-videos skill](skills/editing-videos/SKILL.md)

## Get started

Clone this repo and install both skills for your LLM agent:

```powershell
git clone https://github.com/pritoo733/video-creation-and-editing-skills.git
cd video-creation-and-editing-skills
python scripts/install_skills.py --dest 'YOUR_AGENT_SKILLS_DIRECTORY'
```

Or open the skill you need and add its `SKILL.md` to your agent's instructions.

## What to expect

The workflow helps plan relevant visuals, captions, music, motion, and transitions, then review the exported video. It supports local tools and optional connected services. Tool access, generation limits, and media rights depend on the tools and accounts available to you.

**Google Flow:** the repo can use Flow clips after they are created and exported from Flow. It does not automatically generate or download clips from Flow. Google’s Veo API is a separate service and may charge for generation.

## More

- [Automatic local production](skills/creating-videos/references/automatic-free-production.md)
- [Stock footage and license checks](skills/creating-videos/references/stock-footage.md)
- [Google Flow clip workflow](skills/creating-videos/references/google-flow-workflow.md)
- [Local video dashboard](scripts/video_dashboard.py)
- [Worked example](examples/sample-explainer.md)

---

Provider-neutral workflows do not guarantee a particular creative result. Review each video's accuracy, rights, sound, and playback before publishing.
