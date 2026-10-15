# App Capture Guide

Use this reference for product demos, onboarding videos, and software tutorials filmed from a browser session.

## Before capture

- Confirm the viewer's role and the route through the app. If the intended video is for ordinary users, use their normal portal and permissions; do not substitute an admin view for convenience.
- Use only the authorized logged-in browser/session. Do not ask for, print, or store passwords, session cookies, or access tokens.
- Prepare a screen-by-screen checklist from the script. Mark each shot as required, optional, unsafe, or blocked by unresolved product behavior.
- Use approved demo/test accounts and fictional values. Check that browser notifications, autofill, unrelated tabs, personal bookmarks, and system overlays will not reveal private information.
- Identify consequential controls in advance: Submit, Sign, Send, Approve, Delete, Import, Generate, Payment, Allocate, and configuration Save. Plan a read-only route that stops before any such action unless the user expressly authorizes it.

## During capture

- Start each capture from a recognizable page state. Show the expected navigation path with a steady pointer and short pauses.
- Keep browser chrome when it helps orient the viewer; hide it only when the product context remains clear and no security cue is concealed.
- Do not type into production forms for a demonstration. If typing is needed, use a test environment and fictional data approved for capture.
- Preserve relevant demo/sample notices, empty states, and status labels. Do not make an empty page look populated or imply that a preview is a completed transaction.
- Capture each screen at native resolution. Make separate close-up captures when text must be readable; never upscale tiny text and present it as legible.
- For a page reveal, capture a real scroll with pauses on the sections discussed in the script. A tall full-page screenshot is an alternative for passive content; inspect it for lazy-loading gaps and stitching artifacts. A viewport screenshot alone cannot reveal offscreen content.
- After a sequence, inspect files for readability, stale toasts, personal data, unexpected state changes, and missing screens. Record every rejected capture and why it was replaced.

## After capture

Plan the edit with [interface framing and scrolling](../../editing-videos/references/interface-motion.md). Keep ordinary UI shots at a fixed, readable scale. Use a full-width scrolling viewport to reveal a tall capture, with a short initial hold, a smooth vertical move, and a final reading hold. Use a real recording for sticky headers, nested panels, or interaction. Allocate enough time for the content instead of forcing the move into a short montage slot.

Maintain an asset index with file name, role, app area, capture date, source environment, short description, and any masking applied. Blur only exposed sensitive values and transient personal content; retain a clean source copy in protected project storage. Log what was obscured and verify the blur in the final render.

Treat the walkthrough as a snapshot. Recheck changing labels, availability, prices, rates, permissions, and workflows before a later recording. The UI proves what appeared in that capture, not that a business process completed successfully.
