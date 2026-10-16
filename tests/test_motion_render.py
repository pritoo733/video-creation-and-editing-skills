"""Browser integration checks for the local motion host; no remote assets fetched."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / 'skills/creating-videos/scripts/render_motion.cjs'
NODE = shutil.which('node')
HTML = '''<!doctype html><link rel="icon" href="data:,"><canvas width="320" height="180"></canvas><script>
window.MOTION_META={width:320,height:180,fps:5,duration:1,reviewTimes:[0,.4,.8],events:[{frame:2,action:'move'}]};
const canvas=document.querySelector('canvas'), ctx=canvas.getContext('2d');
window.renderFrame=(t)=>{ctx.fillStyle='white';ctx.fillRect(0,0,320,180);ctx.fillStyle='black';ctx.fillRect(10+t*80,20,50,50);};
</script>'''


@unittest.skipUnless(NODE, 'Node.js not installed')
class MotionRenderChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run([NODE, '-e', "const p=require('playwright'); if(!require('node:fs').existsSync(p.chromium.executablePath()))process.exit(2)"], cwd=ROOT, capture_output=True)
        if result.returncode:
            raise unittest.SkipTest('Playwright/Chromium not installed for local integration checks')

    def run_composition(self, html=HTML, extra=()):
        temporary = tempfile.TemporaryDirectory(prefix='motion host ')
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        source = folder / 'index.html'
        source.write_text(html, encoding='utf-8')
        output = folder / 'result.mp4'
        result = subprocess.run([NODE, str(RENDER), str(source), '--output', str(output), *extra], cwd=ROOT, capture_output=True, text=True, timeout=60)
        report = json.loads((folder / 'result-review/review.json').read_text())
        return result, report, output

    def test_seek_reproducibility_and_event_timing_when_fps_changes(self):
        result, report, output = self.run_composition(extra=('--stills-only', '--fps', '10'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['reverse_seek_check'], 'passed')
        self.assertEqual(report['events'][0]['frame'], 4)
        self.assertEqual(report['creative_review'], 'pending')
        self.assertFalse(output.exists())
        frames = sorted((output.parent / 'result-review').glob('frame-*.png'))
        self.assertGreater(len({p.read_bytes() for p in frames}), 1)

    def test_stateful_animation_fails_instead_of_claiming_success(self):
        html = HTML.replace('window.renderFrame=(t)=>', 'let count=0; window.renderFrame=(t)=>').replace('10+t*80', '10+count++')
        result, report, output = self.run_composition(html, ('--stills-only',))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['status'], 'failed')
        self.assertTrue(any('Non-deterministic' in error for error in report['errors']))
        self.assertFalse(output.exists())

    def test_external_asset_is_blocked_and_reported(self):
        html = HTML.replace('<canvas', '<img src="https://not-requested.invalid/image.png"><canvas')
        result, report, output = self.run_composition(html, ('--stills-only',))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['status'], 'failed')
        self.assertFalse(output.exists())

    def test_missing_encoder_fails_without_a_finished_export(self):
        result, report, output = self.run_composition(extra=('--ffmpeg', 'missing-encoder-motion-check'))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['status'], 'failed')
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
