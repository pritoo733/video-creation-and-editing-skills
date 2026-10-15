# Website framing and scrolling

Use for app screenshots, website demonstrations, and long pages. Keep the interface readable and make movement reveal the content being explained.

## Choose the capture

- Record a real browser scroll when demonstrating navigation, sticky headers, nested scrolling panels, video, animation, or changing controls. Pause on a loaded page, scroll to the next relevant section, then settle before the next action. Preserve the authorized browser/session and capture rules in the creating skill's app-capture guide.
- For passive page content, a tall, fully loaded screenshot can move through a fixed viewport. Describe this as a scrolling screenshot in the production record. It represents captured page content; it does not establish that a browser interaction occurred.
- A single viewport screenshot contains no offscreen information. Obtain a full-page capture or an actual scroll recording before promising a reveal. Check for lazy-loaded blanks, repeated sticky elements, missing fonts, stitching seams, and stale overlays in the source.

Capture at a resolution suitable for the final canvas. Prefer a viewport close to the output aspect ratio for recordings. Preserve the full interface width and its orientation cues; padding is acceptable. A small source enlarged to 1080p does not acquire readable text. Recapture or make a deliberate detail view when the source is insufficient.

## Keep the scale steady

Start interface shots at a fixed scale with no decorative zoom. Avoid fill-and-crop framing that cuts off navigation, page titles, controls, or disclosures. A deliberate close-up should establish the full screen first and explain a specific control; return to context afterward. For ordinary interface shots, keep an optional push within 1.00–1.03 and inspect the endpoints for clipping. The local composer requires a nonempty `framing_reason` above that range; a written reason does not replace visual review.

For a scrolling screenshot, fit its full width to the output viewport and move only vertically. Do not first shrink the entire tall page into the canvas, stretch its aspect ratio, or combine scrolling with zoom. Avoid moving the whole browser frame or inventing sticky headers. When authentic sticky behavior matters, use a recording.

## Plan a readable reveal

Choose start and end sections from the narration, then allocate time for the distance and text density. Hold briefly before moving and after arriving. Ease into and out of the movement, move in one direction, and pause on the information being explained. For multiple reading stops, use an editor's position keyframes or an actual scroll recording; the local image mode supports one move with endpoint holds.

Do not sweep a long page from top to bottom in a two-second montage slot. Select a smaller range, extend the scene, or show a separate relevant section. A continuous reading scene can exceed the promotional cut cadence: add `reading_reason` to document why the interface needs that time. The sequence audit accepts a single long interface shot with this explanation, while still checking adjacent repetition. Inspect the actual reading time; metadata cannot establish it.

Place captions, highlights, and persistent notices outside the active reading area. Preserve relevant demo/sample disclosures. If a notice must remain visible while the captured page scrolls, add an accurate editorial notice in reserved space and record that treatment.

## Local composer example

Mark UI assets with `content_type: "interface"` or a `screen_id`. Without an explicit fit or motion, the composer uses `contain` and no animation. Other content retains its existing defaults. A captured scroll video uses `type: "video"` with these UI markers and no synthetic scroll motion.

For a tall local image:

```json
{
  "path": "captures/help-full-page.png",
  "type": "image",
  "kind": "owned",
  "content_type": "interface",
  "screen_id": "help-page",
  "duration": 7,
  "purpose": "Reveal the two setup steps described in the narration",
  "visual_id": "help-setup-reveal",
  "beat_id": "setup-steps",
  "source_id": "help-full-page",
  "visual_action": "The viewport scrolls from the first setup step to the next",
  "why_it_fits": "Each instruction enters view as the narration introduces it",
  "reading_reason": "Keep the instructions visible through the explanation and final pause",
  "motion": {
    "type": "scroll",
    "from_y": 0.10,
    "to_y": 0.35,
    "hold_start": 0.6,
    "hold_end": 0.8,
    "easing": "smoothstep"
  }
}
```

`from_y` and `to_y` are fractions of the available vertical overflow: 0 is the top and 1 is the bottom. Reverse the values to scroll upward. Choose them after inspecting source dimensions and the relevant sections; the example fractions are illustrative. The source is scaled to the output width, with the output canvas height defining the viewport. `fit` and `focus_x`/`focus_y` do not apply to this scrolling mode. The image must be taller than that viewport after scaling, which the renderer checks with FFmpeg.

The default holds are 0.4 seconds each and the default easing is `smoothstep`; `linear` is available when needed. Holds must leave movement time before the last output frame. Zoom settings cannot be combined with scrolling. Preview scaling changes the viewport proportionally. The edit record preserves the motion configuration, fit, framing reason, and reading reason.

## Review

Inspect the source and the start, middle, and final output frames at the intended playback size. Confirm constant text size, preserved horizontal edges, correct direction and destination, readable endpoint holds, and no blank or invented content. Play the movement at normal speed when available to assess smoothness, pauses, and narration timing; still frames alone cannot establish these. Revise the range or duration when viewers would need to chase the text. Verify captions and disclosures remain clear throughout the move.
