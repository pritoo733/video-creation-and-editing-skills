"""Check that real output ducks music during speech and preserves duration."""
import array
import importlib.util
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

SCRIPT=Path(__file__).resolve().parents[1]/'skills/editing-videos/scripts/mix_audio.py'
spec=importlib.util.spec_from_file_location('mixer',SCRIPT)
mixer=importlib.util.module_from_spec(spec);spec.loader.exec_module(mixer)
FF=os.environ.get('FFMPEG_BIN') or shutil.which('ffmpeg')


@unittest.skipUnless(FF,'Set FFMPEG_BIN for real audio checks')
class MixChecks(unittest.TestCase):
    def test_music_ducks_during_speech_and_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name,freq,duration in [('voice',1000,1),('music',200,3)]:
                subprocess.run([FF,'-v','error','-y','-f','lavfi','-i',f'sine=frequency={freq}:sample_rate=48000:duration={duration}',str(root/(name+'.wav'))],check=True)
            out=root/'mix.wav'
            mixer.mix([dict(path=str(root/'voice.wav'),role='narration',start=1,duration=1),
                       dict(path=str(root/'music.wav'),role='music',duration=3,gain_db=-6)],3,out,FF)
            with wave.open(str(out)) as sound:
                self.assertEqual(sound.getnframes(),3*48000)
                samples=array.array('h',sound.readframes(sound.getnframes()))[::2]
            def level(start,freq):
                part=samples[round(start*48000):round((start+.2)*48000)]
                return abs(sum(v*complex(math.cos(2*math.pi*freq*i/48000),math.sin(2*math.pi*freq*i/48000)) for i,v in enumerate(part)))/len(part)
            before=level(.4,200); during=level(1.4,200); after=level(2.7,200)
            self.assertLess(during,before*.65)
            self.assertGreater(after,during*1.5)
            self.assertGreater(level(1.4,1000),during)
            self.assertLessEqual(max(abs(x) for x in samples),round(.85*32768))


if __name__=='__main__':unittest.main()
