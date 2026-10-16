"""Observable promise/evidence checks and unit-explicit retention analysis."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    item = importlib.util.module_from_spec(spec); spec.loader.exec_module(item)
    return item


hooks = module('hook_workbench', 'skills/creating-videos/scripts/hook_workbench.py')
retention = module('analyze_retention', 'skills/editing-videos/scripts/analyze_retention.py')
SAMPLE = ROOT / 'skills/creating-videos/assets/script-package.example.json'


class HookPlanChecks(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(SAMPLE.read_text(encoding='utf-8'))

    def review(self):
        return hooks.review(self.plan, SAMPLE.parent)

    def test_all_21_categories_are_available_and_sample_retains_editorial_review(self):
        catalog = json.loads(hooks.CATALOG.read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['hooks']), 21)
        self.assertEqual(len({h['id'] for h in catalog['hooks']}), 21)
        result = self.review()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'editorial_review_required')

    def test_selected_hook_needs_an_existing_payoff_with_a_deliverable(self):
        for change in ('missing', 'unexplained'):
            with self.subTest(change=change):
                plan = copy.deepcopy(self.plan)
                if change == 'missing': plan['hooks'][0]['payoff_beat_id'] = 'absent'
                else: del plan['beats'][2]['delivers']
                self.assertEqual(hooks.review(plan, SAMPLE.parent)['status'], 'needs_revision')

    def test_source_existence_and_review_flags_are_required_for_proof(self):
        for source in ({'path':'missing-proof.png','reviewed':True}, {'path':'motion-starter/index.html','reviewed':False}):
            with self.subTest(source=source):
                self.plan['sources']['study'] = source
                self.assertEqual(self.review()['status'], 'needs_revision')

    def test_selected_text_must_be_in_the_actual_opening(self):
        self.plan['beats'][0]['narration'] = 'A different promise has slipped into the script.'
        self.assertEqual(self.review()['status'], 'needs_revision')

    def test_rejected_candidate_does_not_prevent_valid_selected_opening(self):
        self.plan['hooks'][1]['formula_id'] = 'unknown-formula'
        result = self.review()
        self.assertEqual(result['status'], 'editorial_review_required')
        self.assertTrue(result['hooks'][1]['errors'])

    def test_gap_or_nonfinite_timing_cannot_be_treated_as_complete(self):
        for start in (9, float('nan')):
            with self.subTest(start=start):
                self.plan['beats'][1]['start'] = start
                self.assertEqual(self.review()['status'], 'needs_revision')

    def test_repeated_thumbnail_text_is_a_hint_and_does_not_become_a_performance_score(self):
        self.plan['thumbnail_text'] = self.plan['title']
        result = self.review()
        self.assertTrue(result['warnings'])
        self.assertEqual(result['status'], 'editorial_review_required')
        self.assertNotIn('score', result)

    def test_a_short_beat_is_flagged_even_when_total_script_has_enough_time(self):
        self.plan['beats'][0]['end'] = 2
        self.plan['beats'][1]['start'] = 2
        result = self.review()
        self.assertEqual(result['status'], 'editorial_review_required')
        self.assertTrue(any(warning.startswith('opening:') for warning in result['warnings']))


class RetentionChecks(unittest.TestCase):
    def test_irregular_samples_are_reported_as_intervals_and_map_to_beats(self):
        rows = [dict(seconds=t, retention_percent=v) for t,v in [(0,100),(10,95),(40,80)]]
        beats = [dict(id='opening',start=0,end=8),dict(id='body',start=8,end=45)]
        result = retention.analyze(rows, beats)
        self.assertEqual(result['first_30s_drop_pp'], 15)
        self.assertEqual(result['largest_declines'][0]['start'], 10)
        self.assertEqual(result['largest_declines'][0]['end'], 40)
        self.assertEqual(result['largest_declines'][0]['beat_ids'], ['body'])

    def test_short_or_partial_observations_do_not_invent_a_30_second_value(self):
        for points in ([(0,100),(10,90)],[(5,95),(40,75)]):
            rows = [dict(seconds=t,retention_percent=v) for t,v in points]
            self.assertIsNone(retention.analyze(rows)['first_30s_drop_pp'])

    def test_replays_above_100_percent_are_valid(self):
        result = retention.analyze([dict(seconds=0,retention_percent=100),dict(seconds=10,retention_percent=125)])
        self.assertEqual(result['largest_declines'], [])
        self.assertEqual(result['change_first_observed_to_last_pp'], 25)

    def test_duplicate_unsorted_negative_or_nonfinite_samples_are_rejected(self):
        for t, value in [(0,90),(-1,90),(10,-1),(float('nan'),90),(10,float('inf'))]:
            with self.subTest(t=t,value=value):
                with self.assertRaises(ValueError):
                    retention.analyze([dict(seconds=0,retention_percent=100),dict(seconds=t,retention_percent=value)])


if __name__ == '__main__':
    unittest.main()
