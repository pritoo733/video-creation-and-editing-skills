"""Meaningful local checks; FFMPEG_BIN selects an existing FFmpeg executable."""
import importlib.util, json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'skills/editing-videos/scripts/compose_video.py'
spec=importlib.util.spec_from_file_location('composer',SCRIPT)
composer=importlib.util.module_from_spec(spec);spec.loader.exec_module(composer)
FF=os.environ.get('FFMPEG_BIN') or shutil.which('ffmpeg')

def ppm(path,color):
    path.write_bytes(b'P6\n64 64\n255\n'+bytes(color)*64*64)

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='video checks ')
        self.base=Path(self.tmp.name);ppm(self.base/'source.ppm',(255,0,0))
        self.data=dict(format=dict(width=64,height=64,fps=10),shots=[dict(path='source.ppm',type='image',duration=1,purpose='Show the test color')])
    def tearDown(self): self.tmp.cleanup()

class ManifestChecks(Fixture):
    def test_transition_overlap_changes_runtime(self):
        self.data['shots'].append(dict(path='source.ppm',duration=1,purpose='Second beat',transition=dict(type='fade',duration=.2)))
        self.assertAlmostEqual(composer.validate(self.data,self.base),1.8)
        self.data['expected_duration']=2
        with self.assertRaisesRegex(ValueError,'Transitions consume overlap'):composer.validate(self.data,self.base)
    def test_unreviewed_stock_is_rejected(self):
        self.data['shots'][0]['kind']='stock'
        with self.assertRaisesRegex(ValueError,'rights record'):composer.validate(self.data,self.base)
    def test_nonfinite_or_off_grid_timing_is_rejected(self):
        for duration in [float('nan'),.01,1.05]:
            self.data['shots'][0]['duration']=duration
            with self.assertRaises(ValueError):composer.validate(self.data,self.base)

@unittest.skipUnless(FF,'Set FFMPEG_BIN to run render integration checks')
class RenderChecks(Fixture):
    def pixel(self,path,t,x=2,y=2):
        r=subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-vf',f'crop=2:2:{x}:{y},scale=1:1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True)
        return list(r.stdout[:3])
    def test_real_decode_transition_and_overlay(self):
        video=self.base/'red.mp4'
        subprocess.run([FF,'-v','error','-y','-f','lavfi','-i','color=red:s=64x64:r=10:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(video)],check=True)
        ppm(self.base/'blue.ppm',(0,0,255));ppm(self.base/'green.ppm',(0,255,0))
        subprocess.run([FF,'-v','error','-y','-f','lavfi','-i','sine=frequency=440:duration=0.5',str(self.base/'sound.wav')],check=True)
        (self.base/'captions.ass').write_text('[Script Info]\nPlayResX: 64\nPlayResY: 64\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BorderStyle,Outline,Alignment,MarginL,MarginR,MarginV\nStyle: Default,Arial,10,&H00FFFFFF,&H00000000,1,1,2,2,2,2\n[Events]\nFormat: Layer,Start,End,Style,Text\nDialogue: 0,0:00:00.20,0:00:01.50,Default,Hello\n',encoding='utf-8')
        self.data.update(audio='sound.wav',captions='captions.ass')
        self.data['shots']=[dict(path='red.mp4',type='video',duration=1,purpose='Establish red',overlays=[dict(path='green.ppm',x=16,y=16,width=16,start=0,end=.6,fade=.1,slide_y=0)]),dict(path='blue.ppm',type='image',duration=1,purpose='Resolve into blue',motion=dict(zoom_start=1,zoom_end=1.1),transition=dict(type='fade',duration=.2))]
        self.data['expected_duration']=1.8
        out=self.base/'final.mp4'
        record=composer.render(self.data,self.base,out,self.base/'work',FF)
        self.assertAlmostEqual(record['duration'],1.8)
        red=self.pixel(out,.1);self.assertGreater(red[0],200)
        green=self.pixel(out,.3,20,20);self.assertGreater(green[1],180)
        mix=self.pixel(out,.9);self.assertGreater(mix[0],35);self.assertGreater(mix[2],35)
        blue=self.pixel(out,1.5);self.assertGreater(blue[2],200)
        subprocess.run([FF,'-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
        sound=subprocess.run([FF,'-v','error','-i',str(out),'-map','0:a:0','-ac','1','-ar','8000','-f','s16le','pipe:1'],capture_output=True,check=True)
        self.assertGreaterEqual(len(sound.stdout),int(1.7*8000*2))
    def test_short_source_fails_instead_of_silent_freeze(self):
        source=self.base/'short.mp4'
        subprocess.run([FF,'-v','error','-y','-f','lavfi','-i','testsrc2=s=64x64:r=10:d=0.3','-c:v','libx264',str(source)],check=True)
        self.data['shots'][0].update(path='short.mp4',type='video')
        with self.assertRaisesRegex(RuntimeError,'Source too short'):
            composer.render(self.data,self.base,self.base/'long.mp4',self.base/'work',FF)
        self.assertFalse(list((self.base/'work').glob('shot-000-??????????????.mp4')))

if __name__=='__main__':unittest.main()
