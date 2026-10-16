import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'scripts/install_skills.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)

class InstallationChecks(unittest.TestCase):
    def test_install_is_usable_outside_checkout_and_update_is_explicit(self):
        with tempfile.TemporaryDirectory(prefix='agent install ') as tmp:
            dest=Path(tmp)/'skills'
            installer.install(ROOT,dest)
            self.assertTrue((dest/'creating-videos/assets/templates/shot-list.md').is_file())
            self.assertTrue((dest/'editing-videos/scripts/compose_video.py').is_file())
            self.assertTrue((dest/'creating-videos/scripts/render_motion.cjs').is_file())
            self.assertTrue((dest/'creating-videos/assets/motion-starter/index.html').is_file())
            ref=dest/'creating-videos/references/production-workflow.md'
            self.assertTrue((ref.parent/'../assets/templates/coverage-matrix.md').resolve().is_file())
            motion_ref=dest/'creating-videos/references/motion-design-production.md'
            self.assertIn('../assets/templates/visual-beat-sheet.md',motion_ref.read_text(encoding='utf-8'))
            self.assertTrue((motion_ref.parent/'../assets/motion-starter/index.html').resolve().is_file())
            checked=subprocess.run([sys.executable,str(dest/'creating-videos/scripts/hook_workbench.py'),str(dest/'creating-videos/assets/script-package.example.json')],cwd=tmp,capture_output=True,text=True)
            self.assertEqual(checked.returncode,0,checked.stderr)
            self.assertEqual(json.loads(checked.stdout)['status'],'editorial_review_required')
            with self.assertRaisesRegex(ValueError,'already exists'):installer.install(ROOT,dest)
            installer.install(ROOT,dest,update=True)

if __name__=='__main__':unittest.main()
