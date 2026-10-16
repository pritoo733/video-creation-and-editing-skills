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
import shutil
import subprocess
import sys
import wave
from urllib.parse import urlparse
from storyboard import write_storyboard

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
    pacing=plan.get('pacing',{})
    if not isinstance(pacing,dict):
        raise ValueError('pacing must be an object when provided')
    if pacing.get('profile','standard') not in ('standard','short-form'):
        raise ValueError('pacing.profile must be standard or short-form')
    if plan.get('caption_style','kinetic') not in ('kinetic','clean'):
        raise ValueError('caption_style must be kinetic or clean')
    change_seconds=pacing.get('target_visual_change_seconds',2.5)
    if isinstance(change_seconds,bool) or not isinstance(change_seconds,(int,float)) or not math.isfinite(change_seconds) or not 2<=change_seconds<=3:
        raise ValueError('Short-form target_visual_change_seconds must be between 2 and 3 seconds')
    music=plan.get('music')
    if music not in (None,'original-ambient') and not isinstance(music,dict):
        raise ValueError('music must be null, original-ambient, or a local licensed music object')
    if isinstance(music,dict):
        if not music.get('path') or not isinstance(music.get('rights'),dict):
            raise ValueError('A music object needs a local path and rights record')
        rights=music['rights']
        required=('creator','source_url','license','license_url','checked_on','attribution')
        if any(not isinstance(rights.get(key),str) or not rights[key].strip() for key in required):
            raise ValueError('Music rights need creator, source_url, license, license_url, checked_on, and attribution')
        for key in ('source_url','license_url'):
            parsed=urlparse(rights[key])
            if parsed.scheme!='https' or not parsed.hostname:
                raise ValueError(f'Music rights {key} must be an https URL')
        gain=music.get('gain_db',-22)
        if isinstance(gain,bool) or not isinstance(gain,(int,float)) or not math.isfinite(gain) or not -60<=gain<=0:
            raise ValueError('Music gain_db must be between -60 and 0 dB')
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
            elif visual.get('kind') not in ('process','chart','cycle','comparison'):
                raise ValueError('Use stock, process, chart, cycle, or comparison; no paid generator or silent slide fallback')
            elif visual.get('kind')=='comparison':
                labels=visual.get('labels',[]); details=visual.get('details',[])
                if not isinstance(labels,list) or len(labels)!=2 or not isinstance(details,list) or len(details)!=2 or any(not isinstance(value,str) or not value.strip() for value in details):
                    raise ValueError('Comparison graphics need two labels and two concise detail lines')
            hold_reason=visual.get('hold_reason')
            if hold_reason is not None and (not isinstance(hold_reason,str) or len(hold_reason.strip())<20):
                raise ValueError('A short-form hold_reason must explain what viewers need time to read or understand')
    return w,h,fps


def run(command, **kwargs):
    result=subprocess.run([str(c) for c in command],capture_output=True,**kwargs)
    if result.returncode:
        detail=result.stderr.decode(errors='replace') if isinstance(result.stderr,bytes) else result.stderr
        raise RuntimeError(detail[-1800:])
    return result


def record_stage(output, stage, status, details=None):
    path=Path(output)/'production-log.json'
    entries=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    entries.append(dict(time=datetime.now(timezone.utc).isoformat(),stage=stage,status=status,details=details or {}))
    path.write_text(json.dumps(entries,indent=2),encoding='utf-8')


def voice_duration(path):
    with wave.open(str(path)) as audio:
        return audio.getnframes()/audio.getframerate()


def captions(text, start, speech_duration, max_words=7):
    # Exact source text, approximate intra-sentence timing, explicitly recorded.
    words=text.split(); weights=[max(1,len(word.strip('.,!?;:'))+1) for word in words]
    total=sum(weights) or 1; cursor=start; timed_words=[]
    for word,weight in zip(words,weights):
        end=cursor+speech_duration*weight/total
        timed_words.append(dict(text=word,start=cursor,end=end)); cursor=end
    chunks=[]; current=[]
    for word in timed_words:
        if current and (len(current)>=max_words or len(' '.join(item['text'] for item in current+[word]))>45):
            chunks.append(current); current=[]
        current.append(word)
    if current: chunks.append(current)
    return [dict(start=chunk[0]['start'],end=chunk[-1]['end'],
                 text=' '.join(item['text'] for item in chunk),words=chunk) for chunk in chunks]


def align_script_words(expected, recognized, duration):
    """Keep trustworthy Whisper word times and estimate only mismatched spans."""
    normalize=lambda word: re.sub(r'[^a-z0-9]', '', word.lower())
    expected_norm=[normalize(word) for word in expected]
    recognized_norm=[normalize(word['text']) for word in recognized]
    matcher=difflib.SequenceMatcher(None,expected_norm,recognized_norm,autojunk=False)
    aligned=[None]*len(expected); estimated=set()
    for operation, i1, i2, j1, j2 in matcher.get_opcodes():
        if operation=='equal':
            for offset in range(i2-i1):
                item=recognized[j1+offset]
                start=max(0.0,min(float(duration),float(item['start'])))
                end=max(start,min(float(duration),float(item['end'])))
                aligned[i1+offset]=dict(text=expected[i1+offset],start=start,end=end)
        elif operation=='replace' and i2>i1 and j2>j1:
            start=max(0.0,min(float(duration),min(float(word['start']) for word in recognized[j1:j2])))
            end=max(start,min(float(duration),max(float(word['end']) for word in recognized[j1:j2])))
            weights=[max(1,len(word.strip('.,!?;:'))+1) for word in expected[i1:i2]]
            total=sum(weights) or 1; cursor=start
            for index,weight in zip(range(i1,i2),weights):
                next_time=end if index==i2-1 else cursor+(end-start)*weight/total
                aligned[index]=dict(text=expected[index],start=cursor,end=next_time)
                estimated.add(index); cursor=next_time
        elif operation=='delete':
            estimated.update(range(i1,i2))

    # If recognition missed script words, fill only their local gap. This keeps
    # correct timestamps elsewhere instead of replacing the entire track with
    # character-weighted estimates.
    index=0
    while index<len(aligned):
        if aligned[index] is not None:
            index+=1; continue
        end_index=index+1
        while end_index<len(aligned) and aligned[end_index] is None:
            end_index+=1
        left=float(aligned[index-1]['end']) if index else 0.0
        right=float(aligned[end_index]['start']) if end_index<len(aligned) else float(duration)
        span=max(0.0,right-left)
        weights=[max(1,len(word.strip('.,!?;:'))+1) for word in expected[index:end_index]]
        total=sum(weights) or 1
        if span>0:
            cursor=left
            for offset,weight in enumerate(weights):
                next_time=right if offset==len(weights)-1 else cursor+span*weight/total
                aligned[index+offset]=dict(text=expected[index+offset],start=cursor,end=next_time)
                cursor=next_time
        else:
            # Zero-width recognition gaps cannot be aligned from audio evidence.
            # Give the missing words a short local cue window and flag them.
            window=min(float(duration),max(.16,.12*len(weights)))
            cursor=max(0.0,min(left,right)-window)
            step=window/max(1,len(weights))
            for offset in range(len(weights)):
                aligned[index+offset]=dict(text=expected[index+offset],start=cursor+offset*step,end=min(float(duration),cursor+(offset+1)*step))
                estimated.add(index+offset)
        estimated.update(range(index,end_index))
        index=end_index
    return aligned, sorted(estimated)


def caption_rows_from_words(words, duration, max_words=7, max_chars=45):
    rows=[]; group=[]
    for word in words:
        if group and (len(group)>=max_words or len(' '.join([item['text'] for item in group]+[word['text']]))>max_chars):
            start=float(group[0]['start'])
            end=min(float(duration),max(float(group[-1]['end']),start+.08))
            rows.append(dict(start=start,end=end,text=' '.join(item['text'] for item in group),words=group))
            group=[]
        group.append(word)
    if group:
        start=float(group[0]['start'])
        end=min(float(duration),max(float(group[-1]['end']),start+.08))
        rows.append(dict(start=start,end=end,text=' '.join(item['text'] for item in group),words=group))
    return rows


def inspect_captions(rows, duration):
    errors=[]; warnings=[]
    previous_end=0.0
    for number,row in enumerate(rows,1):
        start=float(row['start']); end=float(row['end']); text=row['text']
        if not math.isfinite(start) or not math.isfinite(end) or start<0 or end<=start or end>duration+.05:
            errors.append(f'cue {number}: invalid timing {start:.3f}–{end:.3f}s for {duration:.3f}s video')
            continue
        if start<previous_end-.05:
            warnings.append(f'cue {number}: overlaps the previous cue')
        cue_duration=end-start
        rate=len(text)/cue_duration
        if cue_duration<.5:
            warnings.append(f'cue {number}: shorter than 0.5 seconds')
        if rate>22:
            warnings.append(f'cue {number}: fast reading rate ({rate:.1f} characters/second)')
        if rate>32:
            errors.append(f'cue {number}: exceeds 32 characters/second')
        if len(text)>90:
            warnings.append(f'cue {number}: long caption line ({len(text)} characters)')
        previous_end=end
    return errors,warnings


def timestamp(value,ass=False):
    scale=100 if ass else 1000; value=round(value*scale)
    hour,value=divmod(value,3600*scale); minute,value=divmod(value,60*scale); second,fraction=divmod(value,scale)
    return f'{hour}:{minute:02}:{second:02}.{fraction:02}' if ass else f'{hour:02}:{minute:02}:{second:02},{fraction:03}'


def ass_color(value,default='#41DDBF'):
    value=value if isinstance(value,str) and re.fullmatch(r'#[0-9a-fA-F]{6}',value) else default
    red,green,blue=(int(value[index:index+2],16) for index in (1,3,5))
    return f'&H00{blue:02X}{green:02X}{red:02X}'


def write_captions(rows,output,w,h,style='kinetic',accent='#41DDBF'):
    (output/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{timestamp(row["start"])} --> {timestamp(row["end"])}\n{row["text"]}' for i,row in enumerate(rows))+'\n',encoding='utf-8')
    fontsize=max(18,round(min(w/1080*54,h/1080*58))); outline=max(2,round(fontsize/19)); shadow=max(1,round(fontsize/29))
    margin_v=round(h*.12); accent_color=ass_color(accent)
    header=(f'[Script Info]\nScriptType: v4.00+\nWrapStyle: 0\nScaledBorderAndShadow: yes\nPlayResX: {w}\nPlayResY: {h}\n'
            '[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n'
            f'Style: Default,Arial,{fontsize},{accent_color},&H00FFFFFF,&H00130E09,&H70000000,-1,0,0,0,100,100,0,0,1,{outline},{shadow},2,{round(w*.08)},{round(w*.08)},{margin_v},1\n'
            '[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n')
    events=[]
    for row in rows:
        text=row['text'].replace('{','').replace('}','').replace('\\','').replace('\n',' ')
        if style=='kinetic':
            tokens=row.get('words') or [dict(text=word,start=row['start'],end=row['end']) for word in text.split()]
            pieces=['{\\fad(90,110)\\fscx96\\fscy96\\t(0,130,\\fscx100\\fscy100)}']
            for index,word in enumerate(tokens):
                word_text=word['text'].replace('{','').replace('}','').replace('\\','')
                next_start=float(tokens[index+1]['start']) if index+1<len(tokens) else float(row['end'])
                span=max(.01,min(float(row['end']),next_start)-float(word['start']))
                centiseconds=max(1,round(span*100))
                pieces.append(f'{{\\kf{centiseconds}}}{word_text}')
                if index+1<len(tokens): pieces.append(' ')
            text=''.join(pieces)
        else:
            text='{\\fad(100,120)}'+text
        events.append(f'Dialogue: 0,{timestamp(row["start"],True)},{timestamp(row["end"],True)},Default,,0,0,0,,{text}\n')
    (output/'captions.ass').write_text(header+''.join(events),encoding='utf-8')


def aligned_captions(ffmpeg,audio,text,output):
    import numpy as np
    from faster_whisper import WhisperModel
    pcm=run([ffmpeg,'-v','error','-i',audio,'-ar','16000','-ac','1','-f','f32le','pipe:1']).stdout
    model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2)
    segments,_=model.transcribe(np.frombuffer(pcm,dtype=np.float32),language='en',beam_size=5,word_timestamps=True,vad_filter=True)
    words=[dict(text=word.word.strip(),start=word.start,end=word.end) for segment in segments for word in (segment.words or [])]
    expected=text.split(); normalize=lambda word: re.sub(r'[^a-z0-9]','',word.lower())
    a=[normalize(word) for word in expected]; b=[normalize(word['text']) for word in words]
    opcodes=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
    differences=[dict(operation=op,expected=' '.join(expected[i:j]),recognized=' '.join(w['text'] for w in words[k:l])) for op,i,j,k,l in opcodes if op!='equal']
    audio_duration=len(pcm)/(16000*4)
    aligned,estimated=align_script_words(expected,words,audio_duration)
    (output/'transcript.json').write_text(json.dumps(dict(words=words,differences=differences,
        alignment='partial' if estimated else 'exact',estimated_script_word_indexes=estimated),indent=2),encoding='utf-8')
    return caption_rows_from_words(aligned,audio_duration),differences


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


def produce(plan,output,runtime,draft_only=False,project_root=None):
    import cv2
    import imagehash
    from PIL import Image, ImageDraw
    from motion_graphics import render as render_graphic
    w,h,fps=validate_plan(plan); output=Path(output).resolve(); output.mkdir(parents=True,exist_ok=True)
    project_root=Path(project_root or output).resolve()
    music_source=None
    if isinstance(plan.get('music'),dict):
        music_source=(project_root/plan['music']['path']).resolve()
        if not music_source.is_file():
            raise ValueError(f'Music file does not exist: {music_source}')
    (output/'production-log.json').write_text('[]',encoding='utf-8')
    record_stage(output,'production_started','running',dict(brief=plan['brief'],paid_services=[]))
    ffmpeg=runtime['ffmpeg']; model=Path(runtime['voice']).resolve()
    pacing=plan.get('pacing',{}); short_form=pacing.get('profile')=='short-form'
    max_visual_seconds=min(3.05,float(pacing.get('target_visual_change_seconds',2.5))+.55) if short_form else None
    tts_engine=runtime.get('tts_engine','piper')
    pocket_model=pocket_voice_state=None
    if tts_engine=='piper':
        if not model.is_file() or not Path(str(model)+'.json').is_file():
            raise ValueError('Run setup_free_tools.py first; a local Piper voice and configuration are required')
    elif tts_engine=='pocket':
        try:
            from pocket_tts import TTSModel
            from scipy.io import wavfile
            import numpy as np
        except ImportError as exc:
            raise ValueError('Pocket TTS is not installed in this runtime; rerun setup_free_tools.py --tts-engine pocket') from exc
        print('Loading Pocket TTS model and voice; first run may download weights from Hugging Face.',flush=True)
        pocket_model=TTSModel.load_model()
        pocket_voice_state=pocket_model.get_state_for_audio_prompt(runtime.get('pocket_voice','alba'))
    else:
        raise ValueError(f'Unsupported local TTS engine: {tts_engine}')
    (output/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    work=output/'working'; work.mkdir(exist_ok=True)
    shots=[]; tracks=[]; rows=[]; assets=[]; used=set(); hashes=[]; cursor=0; candidate_log=[]
    for bi,beat in enumerate(plan['beats']):
        record_stage(output,'narration','running',dict(beat=bi+1,total_beats=len(plan['beats'])))
        print(f'BEAT {bi+1}/{len(plan["beats"])}: local narration',flush=True)
        voice_key=(runtime.get('pocket_voice','alba') if tts_engine=='pocket' else str(model.stat().st_mtime_ns))
        key=hashlib.sha256((beat['narration']+tts_engine+str(voice_key)).encode()).hexdigest()[:16]
        audio=work/(key+'.wav')
        if not audio.exists():
            if tts_engine=='piper':
                run([sys.executable,'-m','piper','--model',model,'--output_file',audio],input=beat['narration'].encode('utf-8'))
            else:
                import torch
                # Pocket TTS generates on a worker thread; avoid inference tensors
                # created here that its worker may need to update in-place.
                with torch.no_grad():
                    samples=pocket_model.generate_audio(pocket_voice_state,beat['narration']).detach().cpu().numpy()
                pcm=np.clip(samples,-1,1)
                wavfile.write(str(audio),pocket_model.sample_rate,(pcm*32767).astype(np.int16))
        spoken=voice_duration(audio); frames=math.ceil((spoken+.35)*fps); duration=frames/fps
        tracks.append(dict(path=str(audio),role='narration',start=cursor,duration=spoken,gain_db=0))
        rows+=captions(beat['narration'],cursor,spoken)
        visuals=beat['visuals']; boundaries=[round(frames*j/len(visuals)) for j in range(len(visuals)+1)]
        for vi,visual in enumerate(visuals):
            shot_duration=(boundaries[vi+1]-boundaries[vi])/fps
            if shot_duration<1:
                raise ValueError('Too many shots for the spoken beat; allow at least one second per visual')
            if short_form and shot_duration>max_visual_seconds and not visual.get('hold_reason'):
                raise ValueError(
                    f'Short-form shot {bi+1}:{vi+1} lasts {shot_duration:.2f}s. '
                    'Split the narration beat or add another distinct, relevant visual to keep changes near every 2–3 seconds. '
                    'Use hold_reason only when viewers truly need extra time to read or understand.'
                )
            sid=f'beat-{bi+1:02}-shot-{vi+1:02}'
            common=dict(visual_id=sid,beat_id=f'beat-{bi+1:02}',duration=shot_duration,
                        purpose=visual['why_it_fits'],why_it_fits=visual['why_it_fits'],
                        visual_action=visual.get('action',visual['why_it_fits']))
            if visual.get('hold_reason'):
                common['hold_reason']=visual['hold_reason']
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
                        preview_path=work/'media'/(asset['id']+'-preview.jpg')
                        image.save(preview_path,quality=90)
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
                shot=dict(common,path=selected['local_path'],type='video',kind='stock',source_id='commons:'+selected['id'],rights=rights,
                          preview_path=str(preview_path),asset_title=selected['title'],asset_license=selected['license'],**{'in':source_in})
            else:
                path=work/(sid+'.mp4')
                render_graphic(visual,shot_duration,w,h,fps,path,ffmpeg,plan.get('palette'))
                preview_path=work/(sid+'-preview.jpg')
                preview(ffmpeg,str(path),shot_duration*.65).save(preview_path,quality=90)
                shot=dict(common,path=str(path),type='video',kind='original',source_id='original:'+sid,preview_path=str(preview_path))
                shot.update(visual_state_changes=len(visual['labels']),reading_reason='Progressive graphic states follow the spoken explanation while leaving a readable hold')
                if len(visuals)==1:
                    shot['content_type']='interface' if visual.get('content_type')=='interface' else 'graphic'
            shots.append(shot)
        cursor+=duration
        record_stage(output,'beat_complete','complete',dict(beat=bi+1,total_beats=len(plan['beats']),elapsed_seconds=cursor))
    (output/'candidate-log.json').write_text(json.dumps(candidate_log,indent=2),encoding='utf-8')
    credits=['# Media credits','Include these credits with distribution. Clips were trimmed/reframed and combined with narration/captions.','']
    for asset in assets:
        credits.append(f'- {asset["title"]} — {asset["author"]}; {asset["page"]}; {asset["license"]}: {asset["license_url"]}')
    if tts_engine=='pocket':
        credits+=['',f'Voice synthesis: Pocket TTS by Kyutai Labs; model weights licensed CC BY 4.0 ({runtime.get("pocket_model", "https://huggingface.co/kyutai/pocket-tts")}).',
                  f'Voice preset: {runtime.get("pocket_voice")}; source {runtime.get("pocket_voice_creator")}; {runtime.get("pocket_voice_license")}; {runtime.get("pocket_voice_catalog")}/{runtime.get("pocket_voice_source")}. Check the exact voice terms and include any required attribution before distribution.']
    else:
        credits+=['','Voice: Piper en_US-ljspeech-high; public-domain LJ Speech dataset. See the runtime model card.']
    credits+=['Generated process, chart, cycle, and comparison graphics: original procedural output.']
    if isinstance(plan.get('music'),dict):
        music=plan['music']; suffix=music_source.suffix.lower() or '.audio'
        local_music=work/('licensed-music'+suffix); shutil.copy2(music_source,local_music)
        rights=music['rights']
        track=dict(path=str(local_music),role='music',start=0,duration=cursor,gain_db=music.get('gain_db',-22),
                   source_path=str(music_source),source_url=rights['source_url'],license=rights['license'],
                   license_url=rights['license_url'],creator=rights['creator'],checked_on=rights['checked_on'],
                   attribution=rights['attribution'],sha256=hashlib.sha256(local_music.read_bytes()).hexdigest())
        tracks.append(track)
        credits.append(f'- Music: {rights["creator"]}; {rights["source_url"]}; {rights["license"]}: {rights["license_url"]}; checked {rights["checked_on"]}. {rights["attribution"]}')
    elif plan.get('music')=='original-ambient':
        bed=work/'original-ambient.wav'; ambient_bed(bed,cursor)
        tracks.append(dict(path=str(bed),role='music',start=0,duration=cursor,gain_db=-20,
                           note='Simple generated harmonic ambience, not a composed score'))
        credits.append('- Audio bed: original procedural harmonic ambience; no third-party recording.')
    (output/'CREDITS.md').write_text('\n'.join(credits)+'\n',encoding='utf-8')
    board_path=write_storyboard(plan,shots,output)
    footage_fraction=sum(s['duration'] for s in shots if s['kind']=='stock')/cursor
    record_stage(output,'storyboard_ready','ready_for_review',dict(path=board_path,shots=len(shots),footage_fraction=footage_fraction))
    if draft_only:
        report=dict(status='draft',storyboard=board_path,shots=len(shots),duration=cursor,paid_services=[],
                    next_step='Review storyboard.html and revise plan.json; run without --draft-only to render the final video.')
        record_stage(output,'draft_only_complete','ready_for_review',report)
        (output/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2)); return report
    if plan.get('treatment','mixed')=='footage-led' and footage_fraction<.5:
        raise ValueError('A footage-led brief needs at least half its runtime from relevant actual footage')
    record_stage(output,'audio_mix','running',dict(tracks=len(tracks),duration=cursor))
    editing_module('mix_audio').mix(tracks,cursor,work/'mix.wav',ffmpeg)
    print('CHECK: local speech transcription and caption timing',flush=True)
    aligned,differences=aligned_captions(ffmpeg,work/'mix.wav',' '.join(beat['narration'] for beat in plan['beats']),output)
    caption_method='Local ASR word timestamps aligned to the exact narration script'
    if aligned:
        rows=aligned
        transcript=json.loads((output/'transcript.json').read_text(encoding='utf-8'))
        if transcript.get('estimated_script_word_indexes'):
            caption_method=f'Local ASR word timestamps; {len(transcript["estimated_script_word_indexes"])} mismatched script words received local estimated timing and require review'
        elif differences:
            caption_method='Local ASR timestamps; extra recognized speech was excluded from the exact script captions and requires review'
    else:
        caption_method='measured sentence audio; estimated word groups retained because ASR disagreed; review required'
    caption_errors,caption_warnings=inspect_captions(rows,cursor)
    if caption_errors:
        raise ValueError('Caption quality gate failed: '+str(caption_errors))
    palette=plan.get('palette') if isinstance(plan.get('palette'),dict) else {}
    write_captions(rows,output,w,h,plan.get('caption_style','kinetic'),palette.get('accent','#41DDBF'))
    record_stage(output,'captions_checked','complete',dict(method=caption_method,differences=len(differences),warnings=caption_warnings))
    timeline=dict(format=dict(width=w,height=h,fps=fps),expected_duration=cursor,audio=str(work/'mix.wav'),captions=str(output/'captions.ass'),caption_style=plan.get('caption_style','kinetic'),shots=shots)
    audit=editing_module('audit_visual_sequence'); errors,warnings=audit.audit(timeline)
    if errors:
        raise ValueError('Visual sequence needs revision: '+str(errors))
    (output/'timeline.json').write_text(json.dumps(timeline,indent=2),encoding='utf-8')
    (output/'audio-tracks.json').write_text(json.dumps(dict(duration=cursor,tracks=tracks),indent=2),encoding='utf-8')
    final=output/'final.mp4'
    record_stage(output,'final_render','running',dict(shots=len(shots),format=f'{w}x{h}@{fps}'))
    editing_module('compose_video').render(timeline,output,final,work/'render',ffmpeg)
    export_timeline(shots,tracks,fps,output/'editable.otio')
    run([ffmpeg,'-hide_banner','-loglevel','error','-xerror','-i',final,'-f','null','-'])
    cap=cv2.VideoCapture(str(final)); actual=dict(width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),fps=cap.get(cv2.CAP_PROP_FPS)); cap.release()
    if (actual['width'],actual['height'],actual['frames'])!=(w,h,round(cursor*fps)) or abs(actual['fps']-fps)>.01:
        raise RuntimeError('Final stream dimensions, frame count, or cadence do not match the plan')
    record_stage(output,'technical_validation','complete',dict(full_decode=True,streams=actual,duration=cursor))
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
    report=dict(status='ready_for_creative_review',full_decode=True,streams=actual,duration=cursor,shots=len(shots),unique_stock_sources=len(used),
                footage_fraction=footage_fraction,caption_timing=caption_method,narration_differences=differences,
                license_check='Commons metadata allowlist with saved evidence; personality/property rights and visual relevance need review',
                creative_review='pending: agent must inspect source/action fit, contact sheet, motion, narration and captions',
                warnings=warnings+caption_warnings,caption_quality=dict(errors=caption_errors,warnings=caption_warnings,
                    asr_differences=len(differences),method=caption_method),
                paid_services=[],sha256=hashlib.sha256(final.read_bytes()).hexdigest())
    record_stage(output,'production_complete','ready_for_creative_review',dict(output=str(final),storyboard=board_path,sha256=report['sha256']))
    (output/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2)); return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--draft-only',action='store_true',help='Collect assets and create a reviewable storyboard without rendering the final video')
    args=parser.parse_args()
    try:
        produce(json.loads(args.plan.read_text(encoding='utf-8-sig')),args.output,json.loads(args.runtime.read_text(encoding='utf-8-sig')),args.draft_only,args.plan.resolve().parent)
    except Exception as exc:
        args.output.mkdir(parents=True,exist_ok=True)
        record_stage(args.output,'production_failed','failed',dict(error=str(exc)))
        (args.output/'review.json').write_text(json.dumps(dict(status='failed',error=str(exc)),indent=2),encoding='utf-8')
        raise
