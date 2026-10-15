"""Checks for narration-linked visual variety in edit manifests."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/editing-videos/scripts/audit_visual_sequence.py"
spec = importlib.util.spec_from_file_location("visual_audit", SCRIPT)
visual_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual_audit)


def shot(visual_id, source_id, duration=2.0, **extra):
    return dict(visual_id=visual_id, beat_id="opening", source_id=source_id,
                visual_action="A visible action", why_it_fits="It supports this spoken beat",
                duration=duration, **extra)


class VisualSequenceChecks(unittest.TestCase):
    def test_distinct_narration_matched_shots_pass(self):
        errors, warnings = visual_audit.audit({"format": {"fps": 30}, "shots": [
            shot("construction-wide", "construction", screen_id="scene-a"),
            shot("plan-detail", "blueprints", screen_id="scene-b"),
        ]})
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_adjacent_reused_source_is_rejected(self):
        errors, _ = visual_audit.audit({"format": {"fps": 30}, "shots": [
            shot("construction-one", "construction", screen_id="scene-a"),
            shot("construction-two", "construction", screen_id="scene-b"),
        ]})
        self.assertTrue(any("preceding full-frame source" in error for error in errors))

    def test_long_beat_needs_more_than_one_shot(self):
        errors, _ = visual_audit.audit({"format": {"fps": 30}, "shots": [
            shot("opening-one", "construction", duration=4.5, screen_id="scene-a"),
        ]})
        self.assertTrue(any("fewer than two distinct visuals" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
