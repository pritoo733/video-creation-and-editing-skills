#!/usr/bin/env python3
"""Compose a shot-based JSON timeline with local FFmpeg. Python standard library only."""
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

TRANSITIONS = {'fade', 'dissolve', 'wipeleft', 'wiperight', 'slideleft', 'slideright', 'smoothleft', 'smoothright', 'circleopen', 'fadeblack', 'cut'}

def number(value, label, low=0, high=float('inf')):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{label}: expected a finite number in [{low}, {high}]')
    return value

def media_path(base, value):
    p = (base / value).resolve()
    if not p.is_file():
        raise ValueError(f'Missing local media: {p}')
    return p

def is_interface(shot):
    return shot.get('content_type') == 'interface' or bool(shot.get('screen_id'))

def shot_fit(shot):
    return shot.get('fit', 'contain' if is_interface(shot) else 'cover')

def image_dimensions(ffmpeg, path):
    result = subprocess.run([ffmpeg, '-hide_banner', '-i', str(path), '-vf', 'showinfo',
                             '-frames:v', '1', '-f', 'null', '-'], capture_output=True, text=True)
    match = re.search(r'\bs:(\d+)x(\d+)\b', result.stderr)
    if result.returncode or not match:
        raise RuntimeError(f'Cannot inspect scroll image dimensions: {path}\n{result.stderr[-1000:]}')
    return tuple(map(int, match.groups()))

def scroll_filter(motion, duration, fps, w, h):
    # Scroll the full-width source before fitting; containing the tall image first
    # would shrink all its text and discard the viewport's scrollable content.
    start = motion.get('hold_start', .4)
    end = motion.get('hold_end', .4)
    span = (round(duration*fps)-1)/fps-start-end
    progress = f'clip((t-{start})/{span},0,1)'
    if motion.get('easing', 'smoothstep') == 'smoothstep':
        progress = f'({progress})*({progress})*(3-2*({progress}))'
    first = motion.get('from_y', 0); last = motion.get('to_y', 1)
    y = f'(ih-oh)*({first}+({last}-{first})*({progress}))'
    return f"scale={w}:-2,crop={w}:{h}:0:'{y}':exact=1"

def validate(data, base):
    fmt = data['format']
    for key in ('width', 'height'):
        value = number(fmt[key], key, 16, 8192)
        if int(value) != value or value % 2:
            raise ValueError(f'{key} must be an even integer')
    fps = number(fmt['fps'], 'fps', 1, 120)
    if not data.get('shots'):
        raise ValueError('At least one shot is required')
    total = 0
    previous = None
    for i, shot in enumerate(data['shots']):
        duration = number(shot['duration'], f'shot {i} duration', 1/fps)
        if abs(duration*fps-round(duration*fps)) > 1e-5:
            raise ValueError(f'shot {i}: duration must align to the output frame grid')
        number(shot.get('in', 0), 'source in')
        if shot.get('type', 'video') not in ('video', 'image'):
            raise ValueError('shot type must be video or image')
        if shot_fit(shot) not in ('cover', 'contain'):
            raise ValueError('fit must be cover or contain')
        media_path(base, shot['path'])
        if not shot.get('purpose'):
            raise ValueError(f'shot {i}: explain its relationship to the story in purpose')
        if shot.get('kind') == 'stock':
            rights = shot.get('rights', {})
            for key in ('source_url', 'license_url', 'checked_on', 'evidence', 'intended_use'):
                if not rights.get(key):
                    raise ValueError(f'shot {i}: missing stock rights record: {key}')
            media_path(base, rights['evidence'])
            if rights.get('status') != 'reviewed':
                raise ValueError(f'shot {i}: stock rights must be reviewed for this use')
        transition = shot.get('transition', {'type': 'cut', 'duration': 0})
        if transition['type'] not in TRANSITIONS:
            raise ValueError(f'Unsupported transition: {transition["type"]}')
        overlap = number(transition.get('duration', 0), 'transition duration')
        if transition['type'] == 'cut' and overlap:
            raise ValueError('A hard cut has zero overlap')
        if i == 0 and overlap:
            raise ValueError('The first shot cannot overlap a previous shot')
        if i and overlap >= min(duration, previous):
            raise ValueError('Transition must be shorter than both adjacent shots')
        if abs(overlap*fps-round(overlap*fps)) > 1e-5:
            raise ValueError('Transition duration must align to the output frame grid')
        for key in ('focus_x', 'focus_y'):
            number(shot.get(key, .5), key, 0, 1)
        if 'motion' in shot:
            motion = shot['motion']
            if not isinstance(motion, dict):
                raise ValueError('motion must be an object')
            mode = motion.get('type', 'zoom')
            if mode == 'scroll':
                if shot.get('type', 'video') != 'image':
                    raise ValueError('scroll motion requires an image; use captured video directly')
                if 'zoom_start' in motion or 'zoom_end' in motion:
                    raise ValueError('scroll motion keeps constant scale; remove zoom settings')
                first = number(motion.get('from_y', 0), 'scroll from_y', 0, 1)
                last = number(motion.get('to_y', 1), 'scroll to_y', 0, 1)
                if first == last:
                    raise ValueError('scroll from_y and to_y must differ; use a static shot to hold')
                start = number(motion.get('hold_start', .4), 'scroll hold_start', 0, duration)
                end = number(motion.get('hold_end', .4), 'scroll hold_end', 0, duration)
                if start+end >= (round(duration*fps)-1)/fps:
                    raise ValueError('scroll holds must leave time to move before the last frame')
                if motion.get('easing', 'smoothstep') not in ('smoothstep', 'linear'):
                    raise ValueError('scroll easing must be smoothstep or linear')
            elif mode == 'zoom':
                for key in ('zoom_start', 'zoom_end'):
                    zoom = number(motion.get(key, 1), key, 1, 3)
                    if is_interface(shot) and zoom > 1.03:
                        reason = shot.get('framing_reason')
                        if not isinstance(reason, str) or not reason.strip():
                            raise ValueError('Interface zoom above 1.03 requires a framing_reason for the intentional close-up')
            else:
                raise ValueError('motion type must be zoom or scroll')
        for overlay in shot.get('overlays', []):
            media_path(base, overlay['path'])
            for key in ('x', 'y'):
                number(overlay.get(key, 0), f'overlay {key}', -8192, 8192)
            if 'width' in overlay: number(overlay['width'], 'overlay width', 1, 8192)
            start=number(overlay.get('start', 0), 'overlay start', 0, duration)
            end=number(overlay.get('end', duration), 'overlay end', start, duration)
            number(overlay.get('fade', .2), 'overlay fade', 0, max(0,(end-start)/2))
            number(overlay.get('slide_y', 24), 'overlay slide', -8192, 8192)
        total += duration - overlap
        previous = duration
    for key in ('audio', 'captions'):
        if data.get(key): media_path(base, data[key])
    if 'expected_duration' in data and abs(total-data['expected_duration']) > 1/fps:
        raise ValueError(f'Timeline is {total:.4f}s; expected {data["expected_duration"]}s. Transitions consume overlap.')
    return total

def execute(command, log, expected_frames=None):
    result = subprocess.run(command, capture_output=True, text=True)
    log.write_text(json.dumps(command, ensure_ascii=False)+'\n'+result.stderr+'\n'+result.stdout, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'FFmpeg failed. See {log}\n{result.stderr[-2000:]}')
    if expected_frames is not None:
        frames = [int(l.split('=')[1]) for l in result.stdout.splitlines() if l.startswith('frame=')]
        if not frames or frames[-1] != expected_frames:
            raise RuntimeError(f'Source too short or timeline mismatch: expected {expected_frames} frames, got {frames[-1:]}. See {log}')

def filter_path(path):
    return str(path).replace('\\', '/').replace(':', '\\:').replace("'", "'\\''")

def render(data, base, output, work, ffmpeg, scale=1):
    total = validate(data, base)
    work.mkdir(parents=True, exist_ok=True)
    fmt = data['format']; fps = fmt['fps']
    w,h = [max(16,round(fmt[k]*scale/2)*2) for k in ('width','height')]
    clips=[]; edit_record=[]; cursor=0
    for i, shot in enumerate(data['shots']):
        path=media_path(base,shot['path']); duration=shot['duration']
        n=round(duration*fps)
        inputs=[path]+[media_path(base,o['path']) for o in shot.get('overlays',[])]
        fingerprint=json.dumps(['cfr-v5-interface-scroll',shot,w,h,fps,str(ffmpeg),[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in inputs]],sort_keys=True)
        digest=hashlib.sha256(fingerprint.encode()).hexdigest()[:14]
        clip=work/f'shot-{i:03}-{digest}.mp4'
        if not clip.exists():
            cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-threads','2']
            if shot.get('type','video')=='image': cmd+=['-loop','1','-framerate',str(fps),'-i',str(path)]
            else: cmd+=['-ss',str(shot.get('in',0)),'-i',str(path)]
            for p in inputs[1:]: cmd+=['-loop','1','-framerate',str(fps),'-i',str(p)]
            motion=shot.get('motion',{}); scrolling=motion.get('type')=='scroll'
            if scrolling:
                sw,sh=image_dimensions(ffmpeg,path)
                if round(sh*w/sw/2)*2 <= h:
                    raise ValueError('A scrolling capture must be taller than its viewport at full-width scale; capture more page content or use a static shot')
                fit=scroll_filter(motion,duration,fps,w,h)
            elif shot_fit(shot)=='contain':
                fit=f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x080f19'
            else:
                fit=f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}:(iw-ow)*{shot.get("focus_x",.5)}:(ih-oh)*{shot.get("focus_y",.5)}'
            # Normalize cadence before scaling: some builds lose the last frame's
            # duration metadata in scale, causing a later fps filter to drop it.
            filters=[f'[0:v]fps={fps},{fit},setsar=1,trim=duration={duration}']
            if motion and not scrolling:
                z0=motion.get('zoom_start',1); z1=motion.get('zoom_end',1)
                filters[0]+=f",scale={w*2}:{h*2},zoompan=z='{z0}+({z1}-{z0})*on/{max(1,n-1)}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={w}x{h}:fps={fps}"
            filters[0]+=',format=yuv420p[v0]'
            current='v0'
            for j, overlay in enumerate(shot.get('overlays',[])):
                start=overlay.get('start',0); end=overlay.get('end',duration); fade=overlay.get('fade',.2)
                ov=f'[{j+1}:v]'
                if 'width' in overlay: ov+=f'scale={round(overlay["width"]*scale)}:-1,'
                ov+='format=rgba'
                if fade: ov+=f',fade=t=in:st={start}:d={fade}:alpha=1,fade=t=out:st={end-fade}:d={fade}:alpha=1'
                ov+=f'[o{j}]'; filters.append(ov)
                x=overlay.get('x',0)*scale;y=overlay.get('y',0)*scale;dy=overlay.get('slide_y',24)*scale
                yexpr=f'{y}+{dy}*(1-clip((t-{start})/{max(fade,.01)},0,1))'
                nxt=f'v{j+1}'
                filters.append(f"[{current}][o{j}]overlay=x={x}:y='{yexpr}':enable='between(t,{start},{end})':eof_action=pass[{nxt}]")
                current=nxt
            pending=clip.with_name(clip.stem+'-pending.mp4')
            cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map',f'[{current}]','-an','-r',str(fps),'-fps_mode','cfr','-t',str(duration),'-frames:v',str(n),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','2','-progress','pipe:1','-nostats',str(pending)]
            execute(cmd,work/f'shot-{i:03}.log',n)
            pending.replace(clip)
        transition=shot.get('transition',{'type':'cut','duration':0})
        cursor-=transition.get('duration',0)
        edit_record.append(dict(index=i,start=cursor,end=cursor+duration,source=str(path),source_in=shot.get('in',0),type=shot.get('type','video'),kind=shot.get('kind','owned'),purpose=shot['purpose'],visual_id=shot.get('visual_id'),beat_id=shot.get('beat_id'),source_id=shot.get('source_id'),screen_id=shot.get('screen_id'),content_type=shot.get('content_type'),fit='width' if shot.get('motion',{}).get('type')=='scroll' else shot_fit(shot),motion=shot.get('motion',{}),framing_reason=shot.get('framing_reason'),reading_reason=shot.get('reading_reason'),visual_action=shot.get('visual_action'),why_it_fits=shot.get('why_it_fits'),transition=transition))
        cursor+=duration;clips.append(clip)
        print(f'SHOT {i+1}/{len(data["shots"])} {duration:.2f}s',flush=True)
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y']
    for clip in clips: cmd+=['-i',str(clip)]
    if data.get('audio'): cmd+=['-i',str(media_path(base,data['audio']))]
    hard_cuts=all(shot.get('transition',{'type':'cut','duration':0}).get('duration',0)==0 for shot in data['shots'][1:])
    if hard_cuts:
        # The normalized shot files are already CFR at the target fps. Concatenating
        # all of them in one filter preserves every frame; serial pairwise concat
        # plus repeated fps/timebase conversion can lose frames at each boundary.
        filters=[f'[{i}:v]format=yuv420p[s{i}]' for i in range(len(clips))]
        joined=''.join(f'[s{i}]' for i in range(len(clips)))
        filters.append(f'{joined}concat=n={len(clips)}:v=1:a=0[sequence]')
        current='sequence'
    else:
        filters=[f'[{i}:v]format=yuv420p,fps={fps},settb=AVTB[s{i}]' for i in range(len(clips))]
        current='s0'; length=data['shots'][0]['duration']
        for i,shot in enumerate(data['shots'][1:],1):
            trans=shot.get('transition',{'type':'cut','duration':0}); overlap=trans.get('duration',0); nxt=f'join{i}'
            if not overlap: filters.append(f'[{current}][s{i}]concat=n=2:v=1:a=0,fps={fps},settb=AVTB[{nxt}]')
            else: filters.append(f'[{current}][s{i}]xfade=transition={trans["type"]}:duration={overlap}:offset={length-overlap}[{nxt}]')
            length+=shot['duration']-overlap;current=nxt
    if data.get('captions'):
        filters.append(f"[{current}]subtitles=filename='{filter_path(media_path(base,data['captions']))}'[captioned]")
        current='captioned'
    cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map',f'[{current}]']
    if data.get('audio'):
        cmd+=['-map',f'{len(clips)}:a:0','-af',f'apad,atrim=duration={total},loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000']
    else: cmd+=['-an']
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd+=['-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-threads','4','-r',str(fps),'-fps_mode','cfr','-t',str(total),'-frames:v',str(round(total*fps)),'-movflags','+faststart','-progress','pipe:1','-nostats',str(output)]
    execute(cmd,work/'assembly.log',round(total*fps))
    record=dict(output=str(output),duration=total,format=dict(width=w,height=h,fps=fps),shots=edit_record,review_status='rendered; requires visual and audio review')
    output.with_suffix('.edit.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--ffmpeg',default=shutil.which('ffmpeg'))
    p.add_argument('--workdir',type=Path);p.add_argument('--scale',type=float,default=1)
    p.add_argument('--validate-only',action='store_true')
    args=p.parse_args(); manifest=args.manifest.resolve()
    data=json.loads(manifest.read_text(encoding='utf-8-sig')); duration=validate(data,manifest.parent)
    if args.validate_only: print(f'Valid manifest; {duration:.3f}s. Rights records checked for completeness, not independently verified.');return
    if not args.ffmpeg: p.error('Install FFmpeg or supply --ffmpeg /path/to/ffmpeg')
    number(args.scale,'scale',.1,2)
    output=args.output.resolve();work=args.workdir or output.parent/(output.stem+'-working')
    record=render(data,manifest.parent,output,work.resolve(),str(args.ffmpeg),args.scale)
    print(json.dumps(record,indent=2))

if __name__=='__main__': main()
