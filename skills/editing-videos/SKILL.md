---
name: editing-videos
description: Use when an existing assembled video or cut needs revisions, recutting, captioning, enhancement, review, or export. For making a new video from an idea or raw footage, use creating-videos.
---

# Editing Videos

Make changes for the user's creative goal and intended destination, preserve meaningful source context, and deliver a reviewed export with enough edit data for revisions. Read [the review checklist](references/review-checklist.md) for the full quality gate. Read [the local rendering guide](references/local-rendering.md) when using Piper, FFmpeg, or a frame-based local workflow.

For a footage-led timeline with local media, use [shot composition](references/shot-composition.md) for the optional manifest renderer, timed overlays, transitions, caching, and motion diagnostics. Choose real source actions and edit points before styling; a sequence of animated text layouts is insufficient when the brief calls for a film.

## Edit contract

Before editing, identify the source, current cut, requested changes, audience, destination, creative intent, and protected shots/audio/wording. Keep originals. Record affected ranges and changes in an edit manifest or existing editor timeline.

Check that the media opens and note its duration, frame size, frame rate, orientation, audio channels, and available free storage before choosing an edit path. Confirm the actual editor/encoder capabilities and platform support; do not assume a plugin, model, font, or export feature is installed. Preserve an untouched source and work in a project copy or reversible timeline. Do not silently install software or upload source media to an external service; explain the setup or upload and obtain authorization where needed. See [the editing preflight](references/editing-preflight.md).

For personal stories, preserve the speaker's meaning and the emotional reason behind the material. For factual or commercial work, preserve qualifications and evidence. For app footage, retain meaningful labels, disclosures, and UI context. Document masking, cropping, generated shots, and replacements. Regenerate captions after any timing or dialogue change.

Make one representative edit first when the change introduces a new treatment. Review it at intended playback size before applying it throughout. Use available local tools where practical; check cost and authorization before external processing.

## Delivery gate

Deliver only the current export. Verify that it opens, has the expected duration, dimensions, frame rate, and audio/caption streams, and that the final words are complete. Review the rendered result for visual continuity, caption sync/readability, voice quality, sensitive content, and compliance with the requested treatment. State which checks were performed and which were unavailable. Do not equate a successful render or codec check with a creative review.
