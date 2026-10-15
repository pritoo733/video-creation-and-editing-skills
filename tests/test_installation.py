import importlib.util, tempfile, unittest
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
            ref=dest/'creating-videos/references/production-workflow.md'
            self.assertTrue((ref.parent/'../assets/templates/coverage-matrix.md').resolve().is_file())
            with self.assertRaisesRegex(ValueError,'already exists'):installer.install(ROOT,dest)
            installer.install(ROOT,dest,update=True)

if __name__=='__main__':unittest.main()
