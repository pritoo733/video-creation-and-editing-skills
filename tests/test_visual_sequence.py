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

    def test_readable_interface_scroll_can_keep_a_continuous_beat(self):
        page=shot("page-reveal", "help-page", duration=7, content_type="interface",
                  motion={"type": "scroll", "from_y": .1, "to_y": .3},
                  reading_reason="Keep the two instructions visible while each is explained")
        errors, warnings=visual_audit.audit({"format": {"fps": 30}, "shots": [page]})
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        del page['reading_reason']
        self.assertTrue(visual_audit.audit({"shots": [page]})[0])

    def test_unexplained_interface_crop_and_fast_scroll_are_flagged(self):
        page=shot("page-reveal", "help-page", content_type="interface", fit="cover",
                  motion={"type": "scroll"})
        _, warnings=visual_audit.audit({"shots": [page]})
        self.assertTrue(any("scroll" in warning and "pace" in warning for warning in warnings))
        page['motion']={"zoom_start": 1, "zoom_end": 1.02}
        _, warnings=visual_audit.audit({"shots": [page]})
        self.assertTrue(any("crop" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
