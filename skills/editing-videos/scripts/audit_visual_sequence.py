#!/usr/bin/env python3
"""Audit shot variety and narration links in a local video manifest."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

def interface_shot(shot):
    return shot.get("content_type") == "interface" or bool(shot.get("screen_id"))


def audit(data):
    shots = data.get("shots", [])
    errors, warnings = [], []
    seen_ids = set()
    beat_shots = defaultdict(list)
    beat_order = []
    for i, shot in enumerate(shots):
        label = f"shot {i + 1}"
        motion = shot.get("motion") if isinstance(shot.get("motion"), dict) else {}
        if interface_shot(shot):
            if motion.get("type") == "scroll":
                if float(shot.get("duration", 0)) < 3:
                    warnings.append(f"{label}: short interface scroll; inspect its pace and reading pauses")
            elif shot.get("fit") == "cover":
                reason = shot.get("framing_reason")
                if not isinstance(reason, str) or not reason.strip():
                    warnings.append(f"{label}: interface cover fit can crop controls; use contain or explain the detail framing")
        for key in ("visual_id", "beat_id", "source_id", "visual_action", "why_it_fits"):
            if not isinstance(shot.get(key), str) or not shot[key].strip():
                errors.append(f"{label}: missing {key}")
        visual_id = shot.get("visual_id")
        if visual_id:
            if visual_id in seen_ids:
                errors.append(f"{label}: visual_id repeats {visual_id!r}")
            seen_ids.add(visual_id)
        beat = shot.get("beat_id")
        if beat:
            if beat not in beat_shots:
                beat_order.append(beat)
            beat_shots[beat].append((i, shot))
        if i:
            previous = shots[i - 1]
            if shot.get("source_id") == previous.get("source_id"):
                errors.append(f"{label}: repeats the preceding full-frame source")
            if shot.get("screen_id") and shot.get("screen_id") == previous.get("screen_id"):
                errors.append(f"{label}: repeats the preceding product screenshot")
            if shot.get("visual_id") and shot.get("visual_id") == previous.get("visual_id"):
                errors.append(f"{label}: repeats the preceding visual")
    # Beat IDs describe contiguous narration groups, not recurring chapter labels.
    if len(beat_order) != len(set(beat_order)):
        errors.append("beat_id groups must be contiguous; a narration beat reappears later")
    fps = float(data.get("format", {}).get("fps", 30))
    for beat, items in beat_shots.items():
        duration = sum(float(shot.get("duration", 0)) for _, shot in items)
        distinct = len({shot.get("visual_id") for _, shot in items})
        reading_beat = all((interface_shot(shot) or (shot.get('kind')=='original' and shot.get('visual_state_changes',0)>=2)) and isinstance(shot.get("reading_reason"), str)
                           and shot["reading_reason"].strip() for _, shot in items)
        if duration >= 4 and distinct < 2 and not reading_beat:
            errors.append(f"beat {beat!r}: {duration:.2f}s has fewer than two distinct visuals")
        if any(float(shot.get("duration", 0)) * fps < fps for _, shot in items):
            warnings.append(f"beat {beat!r}: a shot is shorter than one second; confirm it remains readable")
        sources = [shot.get("source_id") for _, shot in items]
        if len(sources) > 2 and len(set(sources)) == 1:
            errors.append(f"beat {beat!r}: one full-frame source carries the whole multi-shot beat")
    # Warn when a source recurs very soon, even if another shot separates it.
    for i, shot in enumerate(shots):
        for j in range(i + 2, min(i + 4, len(shots))):
            if shot.get("source_id") == shots[j].get("source_id"):
                warnings.append(f"shots {i + 1} and {j + 1}: source repeats within three cuts")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", type=Path, help="also save the audit result as JSON")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    errors, warnings = audit(data)
    report = {"shots": len(data.get("shots", [])), "errors": errors, "warnings": warnings,
              "status": "needs revision" if errors else "editorial review required"}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
