"""Execute an agent-authored brief/shot plan with no supplied footage or paid API."""
import argparse
import difflib
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import wave

from free_media import search, rank, download


def editing_module(name):
    path=Path(__file__).resolve().parents[2]/'editing-videos/scripts'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def validate_plan(plan):
    if plan.get('paid_services'):
        raise ValueError('This workflow permits no paid services')
    if not plan.get('brief', '').strip() or not plan.get('beats'):
        raise ValueError('An audience/purpose brief and narration beats are required')
    fmt=plan.get('format',{}); w=fmt.get('width',1920); h=fmt.get('height',1080); fps=fmt.get('fps',30)
    for value in (w,h):
        if not isinstance(value,int) or isinstance(value,bool) or not 320<=value<=3840 or value%2:
            raise ValueError('Use even canvas dimensions from 320 to 3840')
    if fps not in (24,25,30,50,60):
        raise ValueError('Use a supported integer frame rate')
    for beat in plan['beats']:
        if not isinstance(beat.get('narration'),str) or not 1<=len(beat['narration'].split())<=45:
            raise ValueError('Each narration beat needs one to 45 words')
        if not 1<=len(beat.get('visuals',[]))<=4:
            raise ValueError('Each beat needs one to four distinct visuals')
        for visual in beat['visuals']:
            if not visual.get('why_it_fits','').strip():
                raise ValueError('Every visual needs a narration-specific why_it_fits')
            if visual.get('kind')=='stock':
                if not visual.get('query','').strip():
                    raise ValueError('Stock visuals need a subject/action search query')
            elif visual.get('kind') not in ('process','chart'):
                raise ValueError('Use stock, process, or chart; no paid generator or silent slide fallback')
    return w,h,fps


def run(command, **kwargs):
    result=subprocess.run([str(c) for c in command],capture_output=True,**kwargs)
    if result.returncode:
        detail=result.stderr.decode(errors='replace') if isinstance(result.stderr,bytes) else result.stderr
        raise RuntimeError(detail[-1800:])
    return result


def voice_duration(path):
    with wave.open(str(path)) as audio:
        return audio.getnframes()/audio.getframerate()


def captions(text, start, speech_duration, max_words=7):
    # Exact source text, approximate intra-sentence timing, explicitly recorded.
    words=text.split(); chunks=[]; current=[]
    for word in words:
        if current and (len(current)>=max_words or len(' '.join(current+[word]))>45):
            chunks.append(current); current=[]
        current.append(word)
    if current: chunks.append(current)
    weights=[sum(len(word)+1 for word in chunk) for chunk in chunks]; total=sum(weights)
    result=[]; cursor=start
    for chunk,weight in zip(chunks,weights):
        end=cursor+speech_duration*weight/total
        result.append(dict(start=cursor,end=end,text=' '.join(chunk))); cursor=end
    return result


def timestamp(value,ass=False):
    scale=100 if ass else 1000; value=round(value*scale)
    hour,value=divmod(value,3600*scale); minute,value=divmod(value,60*scale); second,fraction=divmod(value,scale)
    return f'{hour}:{minute:02}:{second:02}.{fraction:02}' if ass else f'{hour:02}:{minute:02}:{second:02},{fraction:03}'


def write_captions(rows,output,w,h):
    (output/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{timestamp(row["start"])} --> {timestamp(row["end"])}\n{row["text"]}' for i,row in enumerate(rows))+'\n',encoding='utf-8')
    header=f'[Script Info]\nPlayResX: {w}\nPlayResY: {h}\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\nStyle: Default,Arial,{round(w/1920*38)},&H00FFFFFF,&H00100905,1,2,1,2,{round(w*.07)},{round(w*.07)},{round(h*.07)}\n[Events]\nFormat: Layer,Start,End,Style,Text\n'
    (output/'captions.ass').write_text(header+''.join(f'Dialogue: 0,{timestamp(row["start"],True)},{timestamp(row["end"],True)},Default,{row["text"].replace(chr(10)," ").replace("{","").replace("}","").replace(chr(92),"")}\n' for row in rows),encoding='utf-8')


def aligned_captions(ffmpeg,audio,text,output):
    import numpy as np
    from faster_whisper import WhisperModel
    pcm=run([ffmpeg,'-v','error','-i',audio,'-ar','16000','-ac','1','-f','f32le','pipe:1']).stdout
    model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2)
    segments,_=model.transcribe(np.frombuffer(pcm,dtype=np.float32),language='en',beam_size=5,word_timestamps=True,vad_filter=True)
    words=[dict(text=word.word.strip(),start=word.start,end=word.end) for segment in segments for word in (segment.words or [])]
    expected=text.split(); normalize=lambda word: re.sub(r'[^a-z0-9]','',word.lower())
    a=[normalize(w) for w in expected]; b=[normalize(w['text']) for w in words]
    differences=[dict(operation=op,expected=' '.join(expected[i:j]),recognized=' '.join(w['text'] for w in words[k:l])) for op,i,j,k,l in difflib.SequenceMatcher(None,a,b).get_opcodes() if op!='equal']
    (output/'transcript.json').write_text(json.dumps(dict(words=words,differences=differences),indent=2),encoding='utf-8')
    if differences:
        return None,differences
    result=[]; group=[]
    for original,word in zip(expected,words):
        if group and (len(group)>=7 or len(' '.join([w['text'] for w in group]+[original]))>45):
            result.append(dict(start=group[0]['start'],end=group[-1]['end'],text=' '.join(w['text'] for w in group))); group=[]
        group.append(dict(word,text=original))
    if group: result.append(dict(start=group[0]['start'],end=group[-1]['end'],text=' '.join(w['text'] for w in group)))
    return result,[]


def source_interval(path, duration):
    from scenedetect import detect, AdaptiveDetector
    scenes=detect(str(path),AdaptiveDetector())
    usable=[(a.get_seconds(),b.get_seconds()) for a,b in scenes if b.get_seconds()-a.get_seconds()>=duration+.2]
    # PySceneDetect reports only cut boundaries. An uninterrupted clip has no
    # boundaries and therefore returns []; that is one valid scene, not zero.
    if not scenes:
        import cv2
        cap=cv2.VideoCapture(str(path))
        try:
            fps=cap.get(cv2.CAP_PROP_FPS); frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
            actual=frames/fps if fps>0 and frames>0 else 0
        finally:
            cap.release()
        if actual>=duration+.2:
            return 0.0
    if not usable:
        raise ValueError('No uninterrupted source interval is long enough for this shot')
    first,last=max(usable,key=lambda x:x[1]-x[0])
    return round((first+min(.5,(last-first-duration)/2))*30)/30


def preview(ffmpeg,path,t,width=480):
    from PIL import Image
    raw=run([ffmpeg,'-hide_banner','-loglevel','error','-ss',str(t),'-i',path,'-frames:v','1',
             '-vf',f'scale={width}:-2','-f','image2pipe','-vcodec','png','pipe:1']).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB')


def ambient_bed(path,duration):
    # Original, intentionally quiet harmonic texture. Opt-in; not downloaded music.
    import array
    rate=48000; samples=array.array('h')
    for i in range(round(duration*rate)):
        t=i/rate; fade=min(1,t/1.5,max(0,(duration-t)/1.5))
        tone=sum(math.sin(2*math.pi*f*t+.1*math.sin(t*.2))/(j+1) for j,f in enumerate((130.8128,164.8138,195.9977)))
        samples.append(round(tone*fade*3500))
    if sys.byteorder!='little': samples.byteswap()
    with wave.open(str(path),'wb') as output:
        output.setparams((1,2,rate,0,'NONE','not compressed')); output.writeframes(samples.tobytes())


def export_timeline(shots,tracks,fps,path):
    import opentimelineio as otio
    time=lambda seconds: otio.opentime.RationalTime(round(seconds*fps),fps)
    timeline=otio.schema.Timeline(name='Automatic production')
    video=otio.schema.Track(name='Picture',kind=otio.schema.TrackKind.Video)
    for shot in shots:
        video.append(otio.schema.Clip(name=shot['visual_id'],media_reference=otio.schema.ExternalReference(target_url=Path(shot['path']).as_uri()),source_range=otio.opentime.TimeRange(time(shot.get('in',0)),time(shot['duration']))))
    timeline.tracks.append(video)
    for i,track in enumerate(tracks):
        audio=otio.schema.Track(name=f'{track["role"]}-{i+1}',kind=otio.schema.TrackKind.Audio)
        if track.get('start',0): audio.append(otio.schema.Gap(source_range=otio.opentime.TimeRange(time(0),time(track['start']))))
        audio.append(otio.schema.Clip(name=track['role'],media_reference=otio.schema.ExternalReference(target_url=Path(track['path']).as_uri()),source_range=otio.opentime.TimeRange(time(track.get('in',0)),time(track['duration']))))
        audio.metadata['mix_settings']=track
        timeline.tracks.append(audio)
    timeline.metadata['limitations']='Captions, ducking, and audio gain require reconstruction in an external editor; preserve the JSON manifests.'
    otio.adapters.write_to_file(timeline,str(path))


def produce(plan,output,runtime):
    import cv2
    import imagehash
    from PIL import Image, ImageDraw
    from motion_graphics import render as render_graphic
    w,h,fps=validate_plan(plan); output=Path(output).resolve(); output.mkdir(parents=True,exist_ok=True)
    ffmpeg=runtime['ffmpeg']; model=Path(runtime['voice']).resolve()
    if not model.is_file() or not Path(str(model)+'.json').is_file():
        raise ValueError('Run setup_free_tools.py first; a local voice and configuration are required')
    (output/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    work=output/'working'; work.mkdir(exist_ok=True)
    shots=[]; tracks=[]; rows=[]; assets=[]; used=set(); hashes=[]; cursor=0; candidate_log=[]
    for bi,beat in enumerate(plan['beats']):
        print(f'BEAT {bi+1}/{len(plan["beats"])}: local narration',flush=True)
        key=hashlib.sha256((beat['narration']+str(model.stat().st_mtime_ns)).encode()).hexdigest()[:16]
        audio=work/(key+'.wav')
        if not audio.exists():
            run([sys.executable,'-m','piper','--model',model,'--output_file',audio],input=beat['narration'].encode('utf-8'))
        spoken=voice_duration(audio); frames=math.ceil((spoken+.35)*fps); duration=frames/fps
        tracks.append(dict(path=str(audio),role='narration',start=cursor,duration=spoken,gain_db=0))
        rows+=captions(beat['narration'],cursor,spoken)
        visuals=beat['visuals']; boundaries=[round(frames*j/len(visuals)) for j in range(len(visuals)+1)]
        for vi,visual in enumerate(visuals):
            shot_duration=(boundaries[vi+1]-boundaries[vi])/fps
            if shot_duration<1:
                raise ValueError('Too many shots for the spoken beat; allow at least one second per visual')
            sid=f'beat-{bi+1:02}-shot-{vi+1:02}'
            common=dict(visual_id=sid,beat_id=f'beat-{bi+1:02}',duration=shot_duration,
                        purpose=visual['why_it_fits'],why_it_fits=visual['why_it_fits'],
                        visual_action=visual.get('action',visual['why_it_fits']))
            if visual['kind']=='stock':
                print('SEARCH: '+visual['query'],flush=True)
                candidates=rank(search(visual['query'],plan.get('minimum_source_width',1280),plan.get('minimum_source_height',720)),visual['query'],shot_duration,used)
                selected=None
                for candidate in candidates[:3]:
                    record={k:v for k,v in candidate.items() if k!='evidence'}
                    try:
                        asset=download(candidate,work/'media')
                        source_in=visual.get('source_in')
                        if source_in is None:
                            source_in=source_interval(asset['local_path'],shot_duration)
                        if not isinstance(source_in,(int,float)) or not math.isfinite(source_in) or source_in<0 or source_in+shot_duration>asset['duration']:
                            raise ValueError('The selected source interval exceeds the clip')
                        image=preview(ffmpeg,asset['local_path'],source_in+shot_duration/2)
                        image.save(work/'media'/(asset['id']+'-preview.jpg'),quality=90)
                        fingerprint=imagehash.phash(image)
                        if any(fingerprint-previous<=4 for previous in hashes):
                            raise ValueError('Near-duplicate visual already selected')
                        hashes.append(fingerprint); used.add(asset['id']); selected=asset
                        record['selection']='selected'; candidate_log.append(record); break
                    except (ValueError,RuntimeError) as exc:
                        record.update(selection='rejected',reason=str(exc)); candidate_log.append(record)
                if selected is None:
                    (output/'candidate-log.json').write_text(json.dumps(candidate_log,indent=2),encoding='utf-8')
                    raise ValueError('No suitable distinct free video found for '+visual['query']+'. Revise the query or explicitly design an original graphic; no slideshow fallback was made.')
                assets.append(selected)
                rights=dict(source_url=selected['page'],license_url=selected['license_url'],checked_on=selected['checked_on'],
                            evidence=selected['evidence_path'],status='metadata-checked',verification_method='commons-api-license-allowlist-v1',
                            intended_use='Edited illustrative context; not a product feature, endorsement, or customer result')
                shot=dict(common,path=selected['local_path'],type='video',kind='stock',source_id='commons:'+selected['id'],rights=rights,**{'in':source_in})
            else:
                path=work/(sid+'.mp4')
                render_graphic(visual,shot_duration,w,h,fps,path,ffmpeg,plan.get('palette'))
                shot=dict(common,path=str(path),type='video',kind='original',source_id='original:'+sid)
                shot.update(visual_state_changes=len(visual['labels']),reading_reason='Progressive diagram/chart states follow the spoken explanation without a disruptive cut')
                if len(visuals)==1:
                    shot['content_type']='interface' if visual.get('content_type')=='interface' else 'graphic'
            shots.append(shot)
        cursor+=duration
    footage_fraction=sum(s['duration'] for s in shots if s['kind']=='stock')/cursor
    if plan.get('treatment','mixed')=='footage-led' and footage_fraction<.5:
        raise ValueError('A footage-led brief needs at least half its runtime from relevant actual footage')
    if plan.get('music')=='original-ambient':
        bed=work/'original-ambient.wav'; ambient_bed(bed,cursor)
        tracks.append(dict(path=str(bed),role='music',start=0,duration=cursor,gain_db=-20))
    editing_module('mix_audio').mix(tracks,cursor,work/'mix.wav',ffmpeg)
    print('CHECK: local speech transcription and caption timing',flush=True)
    aligned,differences=aligned_captions(ffmpeg,work/'mix.wav',' '.join(beat['narration'] for beat in plan['beats']),output)
    caption_method='ASR word timestamps checked against the exact narration script'
    if aligned:
        rows=aligned
    else:
        caption_method='measured sentence audio; estimated word groups retained because ASR disagreed; review required'
    write_captions(rows,output,w,h)
    timeline=dict(format=dict(width=w,height=h,fps=fps),expected_duration=cursor,audio=str(work/'mix.wav'),captions=str(output/'captions.ass'),shots=shots)
    audit=editing_module('audit_visual_sequence'); errors,warnings=audit.audit(timeline)
    if errors:
        raise ValueError('Visual sequence needs revision: '+str(errors))
    (output/'timeline.json').write_text(json.dumps(timeline,indent=2),encoding='utf-8')
    (output/'audio-tracks.json').write_text(json.dumps(dict(duration=cursor,tracks=tracks),indent=2),encoding='utf-8')
    (output/'candidate-log.json').write_text(json.dumps(candidate_log,indent=2),encoding='utf-8')
    credits=['# Media credits','Include these credits with distribution. Clips were trimmed/reframed and combined with narration/captions.','']
    for asset in assets:
        credits.append(f'- {asset["title"]} — {asset["author"]}; {asset["page"]}; {asset["license"]}: {asset["license_url"]}')
    credits+=['','Voice: Piper en_US-ljspeech-high; public-domain LJ Speech dataset. See the runtime model card.',
              'Generated process/chart graphics and optional harmonic bed: original procedural output.']
    (output/'CREDITS.md').write_text('\n'.join(credits)+'\n',encoding='utf-8')
    final=output/'final.mp4'
    editing_module('compose_video').render(timeline,output,final,work/'render',ffmpeg)
    export_timeline(shots,tracks,fps,output/'editable.otio')
    run([ffmpeg,'-hide_banner','-loglevel','error','-xerror','-i',final,'-f','null','-'])
    cap=cv2.VideoCapture(str(final)); actual=dict(width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),fps=cap.get(cv2.CAP_PROP_FPS)); cap.release()
    if (actual['width'],actual['height'],actual['frames'])!=(w,h,round(cursor*fps)) or abs(actual['fps']-fps)>.01:
        raise RuntimeError('Final stream dimensions, frame count, or cadence do not match the plan')
    thumbs=[]; elapsed=0
    for shot in shots:
        for fraction in (.05,.5,.95):
            im=preview(ffmpeg,final,elapsed+shot['duration']*fraction)
            thumbs.append((shot['visual_id'],im))
        elapsed+=shot['duration']
    sheet=Image.new('RGB',(1440,math.ceil(len(thumbs)/3)*300),'#081420'); draw=ImageDraw.Draw(sheet)
    for i,(label,im) in enumerate(thumbs):
        im.thumbnail((470,264)); x=(i%3)*480; y=(i//3)*300; sheet.paste(im,(x,y)); draw.text((x+5,y+270),label,fill='white')
    sheet.save(output/'review-contact-sheet.jpg',quality=92)
    report=dict(full_decode=True,streams=actual,duration=cursor,shots=len(shots),unique_stock_sources=len(used),
                footage_fraction=footage_fraction,caption_timing=caption_method,narration_differences=differences,
                license_check='Commons metadata allowlist with saved evidence; personality/property rights and visual relevance need review',
                creative_review='pending: agent must inspect source/action fit, contact sheet, motion, narration and captions',
                warnings=warnings,paid_services=[],sha256=hashlib.sha256(final.read_bytes()).hexdigest())
    (output/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2)); return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,required=True)
    args=parser.parse_args()
    try:
        produce(json.loads(args.plan.read_text(encoding='utf-8-sig')),args.output,json.loads(args.runtime.read_text(encoding='utf-8-sig')))
    except Exception as exc:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'review.json').write_text(json.dumps(dict(status='failed',error=str(exc)),indent=2),encoding='utf-8')
        raise
