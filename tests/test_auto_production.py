"""Observable policy/timing checks for asset-free production; no network in unit tests."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

SCRIPTS=Path(__file__).resolve().parents[1]/'skills/creating-videos/scripts'
sys.path.insert(0,str(SCRIPTS))
import free_media
import auto_produce
import motion_graphics


def page():
    return dict(pageid=12,title='File:Ocean.webm',imageinfo=[dict(url='https://upload.wikimedia.org/wikipedia/commons/a/aa/Ocean.webm',
                descriptionurl='https://commons.wikimedia.org/wiki/File:Ocean.webm',width=1920,height=1080,duration=12,size=1000000,mime='video/webm',
                extmetadata=dict(LicenseShortName={'value':'CC BY 4.0'},LicenseUrl={'value':'https://creativecommons.org/licenses/by/4.0/'},Artist={'value':'<a>Test creator</a>'}))])


class MediaPolicyChecks(unittest.TestCase):
    def test_free_attributed_video_preserves_source_and_credit(self):
        item=free_media.normalize(page())
        self.assertEqual(item['author'],'Test creator')
        self.assertEqual(item['id'],'12')
        self.assertEqual(item['license_url'],'https://creativecommons.org/licenses/by/4.0/')
    def test_noncommercial_sharealike_and_unknown_terms_are_not_auto_selected(self):
        for label,url in [('CC BY-NC 4.0','https://creativecommons.org/licenses/by-nc/4.0/'),
                          ('CC BY-SA 4.0','https://creativecommons.org/licenses/by/4.0/'),
                          ('Free download','https://example.com/free'),
                          ('CC BY 4.0','https://creativecommons.org.evil.test/licenses/by/4.0/')]:
            with self.subTest(label=label):self.assertFalse(free_media.allowed_license(label,url))
    def test_missing_author_or_extra_restrictions_require_review(self):
        for key,value in [('Artist',''),('Restrictions','Personality rights')]:
            item=page(); item['imageinfo'][0]['extmetadata'][key]={'value':value}
            self.assertIsNone(free_media.normalize(item))
    def test_source_ranking_never_repeats_a_used_asset_or_truncates_it(self):
        first=free_media.normalize(page()); second=dict(first,id='13',duration=1)
        self.assertEqual(free_media.rank([first,second],'ocean',4,{'12'}),[])


class PlanAndCaptionChecks(unittest.TestCase):
    def test_source_free_plan_is_valid_but_paid_service_is_not(self):
        plan=dict(brief='Explain an idea to a new viewer',beats=[dict(narration='A clear sequence makes the process easier to follow.',visuals=[dict(kind='process',labels=['Plan','Create','Review'],why_it_fits='Shows the named stages')])])
        self.assertEqual(auto_produce.validate_plan(plan),(1920,1080,30))
        plan['paid_services']=['paid-video-api']
        with self.assertRaisesRegex(ValueError,'no paid'):auto_produce.validate_plan(plan)
    def test_caption_groups_preserve_every_word_and_measured_sentence_bounds(self):
        text='A complete sentence must keep every word visible in the correct order.'
        rows=auto_produce.captions(text,2.5,5)
        self.assertEqual(' '.join(row['text'] for row in rows),text)
        self.assertEqual(rows[0]['start'],2.5)
        self.assertAlmostEqual(rows[-1]['end'],7.5)
        self.assertTrue(all(a['end']<=b['start']+1e-8 for a,b in zip(rows,rows[1:])))
    def test_uninterrupted_clip_is_treated_as_one_scene(self):
        class Capture:
            def get(self, prop):
                import cv2
                return {cv2.CAP_PROP_FPS:30,cv2.CAP_PROP_FRAME_COUNT:300}.get(prop,0)
            def release(self): pass
        with mock.patch('scenedetect.detect',return_value=[]), mock.patch('cv2.VideoCapture',return_value=Capture()):
            self.assertEqual(auto_produce.source_interval('uninterrupted.webm',5),0)
            with self.assertRaisesRegex(ValueError,'No uninterrupted'):
                auto_produce.source_interval('uninterrupted.webm',10)


class MotionGraphicChecks(unittest.TestCase):
    def test_four_story_graphic_forms_render_deterministic_frames(self):
        specs=[
            dict(kind='process',title='A clear process',labels=['Plan','Make','Review']),
            dict(kind='chart',title='A sourced chart',labels=['A','B'],values=[2,5],source='Source: example'),
            dict(kind='cycle',title='A repeating cycle',center_label='Core',labels=['Start','Change','Return']),
            dict(kind='comparison',title='Before and after',labels=['Before','After'],details=['Separate steps','One clear flow']),
        ]
        for spec in specs:
            with self.subTest(kind=spec['kind']):
                first=motion_graphics.draw_frame(spec,1.2,2.4,640,360,dict(background='#081420',accent='#41ddbf'))
                second=motion_graphics.draw_frame(spec,1.2,2.4,640,360,dict(background='#081420',accent='#41ddbf'))
                self.assertEqual(first.size,(640,360))
                self.assertEqual(first.tobytes(),second.tobytes())

    def test_comparison_requires_two_complete_side_descriptions(self):
        spec=dict(kind='comparison',labels=['Before','After'],details=['Separate steps'])
        with self.assertRaisesRegex(ValueError,'two concise detail lines'):
            motion_graphics.draw_frame(spec,0,2,640,360)


if __name__=='__main__':unittest.main()
