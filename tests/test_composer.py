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
    def test_automated_commons_rights_require_matching_allowlisted_evidence(self):
        evidence=self.base/'license.json'
        url='https://commons.wikimedia.org/wiki/File:Example.webm'
        license_url='https://creativecommons.org/licenses/by/4.0/'
        evidence.write_text(json.dumps(dict(imageinfo=[dict(descriptionurl=url,extmetadata=dict(LicenseUrl={'value':license_url}))])))
        rights=dict(source_url=url,license_url=license_url,checked_on='2026-10-15',evidence='license.json',
                    intended_use='Illustrative context',status='metadata-checked',verification_method='commons-api-license-allowlist-v1')
        self.data['shots'][0].update(kind='stock',rights=rights)
        composer.validate(self.data,self.base)
        rights['license_url']='https://creativecommons.org/licenses/by-nc/4.0/'
        with self.assertRaisesRegex(ValueError,'unsupported automated'):composer.validate(self.data,self.base)
        rights['license_url']=license_url
        evidence.write_text(json.dumps(dict(imageinfo=[dict(descriptionurl='https://example.com/other-file')])))
        with self.assertRaisesRegex(ValueError,'evidence does not match'):composer.validate(self.data,self.base)
    def test_nonfinite_or_off_grid_timing_is_rejected(self):
        for duration in [float('nan'),.01,1.05]:
            self.data['shots'][0]['duration']=duration
            with self.assertRaises(ValueError):composer.validate(self.data,self.base)
    def test_interface_zoom_requires_a_reason_for_a_closeup(self):
        self.data['shots'][0].update(screen_id='dashboard',motion=dict(zoom_start=1,zoom_end=1.25))
        with self.assertRaisesRegex(ValueError,'framing_reason'):
            composer.validate(self.data,self.base)
        self.data['shots'][0]['framing_reason']='Inspect the selected status control in a deliberate detail shot'
        composer.validate(self.data,self.base)
    def test_invalid_scroll_configuration_is_rejected(self):
        shot=self.data['shots'][0]
        cases=[dict(type='scroll',from_y=-.1),dict(type='scroll',to_y=1.1),
               dict(type='scroll',hold_start=.8,hold_end=.8),
               dict(type='scroll',zoom_end=1.1),dict(type='scroll',easing='bounce'),
               dict(type='scroll',from_y=.5,to_y=.5),dict(type='unknown')]
        for motion in cases:
            with self.subTest(motion=motion):
                shot['motion']=motion
                with self.assertRaises(ValueError):composer.validate(self.data,self.base)
        shot.update(type='video',motion=dict(type='scroll'))
        with self.assertRaisesRegex(ValueError,'image'):
            composer.validate(self.data,self.base)

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
    def test_interface_defaults_preserve_both_horizontal_edges(self):
        row=bytes((0,0,255))*16+bytes((255,0,0))*96+bytes((0,255,0))*16
        (self.base/'wide.ppm').write_bytes(b'P6\n128 64\n255\n'+row*64)
        self.data['shots'][0].update(path='wide.ppm',screen_id='dashboard')
        out=self.base/'interface.mp4'
        record=composer.render(self.data,self.base,out,self.base/'work',FF)
        self.assertGreater(self.pixel(out,.5,2,32)[2],200)
        self.assertGreater(self.pixel(out,.5,60,32)[1],200)
        self.assertLess(max(self.pixel(out,.5,32,2)),50)
        self.assertEqual(record['shots'][0]['fit'],'contain')
    def test_scroll_holds_reaches_both_ends_and_keeps_constant_width(self):
        pixels=bytearray()
        for y in range(192):
            color=((255,0,0),(0,255,0),(0,0,255))[y//64]
            pixels+=bytes((255,255,255))*4+bytes(color)*56+bytes((255,255,255))*4
        (self.base/'page.ppm').write_bytes(b'P6\n64 192\n255\n'+pixels)
        motion=dict(type='scroll',from_y=0,to_y=1,hold_start=.3,hold_end=.3,easing='smoothstep')
        self.data['shots'][0].update(path='page.ppm',content_type='interface',duration=2,motion=motion)
        self.data['shots'].append(dict(self.data['shots'][0],motion=dict(motion,from_y=1,to_y=0)))
        out=self.base/'scroll.mp4'
        record=composer.render(self.data,self.base,out,self.base/'work',FF)
        for t,channel in [(0,0),(.2,0),(1,1),(1.7,2),(1.9,2),(2.1,2),(3,1),(3.9,0)]:
            with self.subTest(time=t):
                self.assertGreater(self.pixel(out,t,32,32)[channel],200)
                self.assertGreater(min(self.pixel(out,t,0,32)),200)
                self.assertGreater(min(self.pixel(out,t,62,32)),200)
        self.assertEqual(record['shots'][0]['motion'],motion)
        subprocess.run([FF,'-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
        # Measure the source's colored section boundaries in every decoded frame.
        # This catches reversals, missed endpoint holds, and abrupt start/stop motion.
        raw=subprocess.run([FF,'-v','error','-i',str(out),'-vf','crop=2:64:32:0',
                            '-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
        frame_bytes=2*64*3
        self.assertEqual(len(raw),40*frame_bytes)
        offsets=[]
        for i in range(40):
            frame=raw[i*frame_bytes:(i+1)*frame_bytes]
            rows=[frame[y*6:y*6+3] for y in range(64)]
            red=sum(p[0]>180 and p[2]<60 for p in rows)
            blue=sum(p[2]>180 and p[0]<60 for p in rows)
            offsets.append(64-red if red else 64+blue)
        self.assertEqual(offsets[:3],[0]*3)
        self.assertEqual(offsets[17:20],[128]*3)
        self.assertTrue(all(a<=b for a,b in zip(offsets[:19],offsets[1:20])))
        self.assertTrue(all(a>=b for a,b in zip(offsets[20:39],offsets[21:40])))
        middle_step=offsets[10]-offsets[9]
        self.assertLess(offsets[5]-offsets[4],middle_step)
        self.assertLess(offsets[16]-offsets[15],middle_step)
    def test_scroll_rejects_a_capture_without_vertical_overflow(self):
        self.data['shots'][0]['motion']=dict(type='scroll')
        with self.assertRaisesRegex(ValueError,'taller'):
            composer.render(self.data,self.base,self.base/'scroll.mp4',self.base/'work',FF)

if __name__=='__main__':unittest.main()
