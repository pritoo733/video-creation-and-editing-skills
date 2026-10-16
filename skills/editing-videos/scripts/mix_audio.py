"""Mix local narration, music, ambience, and effect tracks with speech ducking."""
import argparse
import json
import math
from pathlib import Path
import subprocess


def mix(tracks, duration, output, ffmpeg):
    if not tracks or not math.isfinite(duration) or duration <= 0:
        raise ValueError('A positive duration and at least one audio track are required')
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y']
    groups = {'narration': [], 'music': [], 'ambience': [], 'effect': []}
    filters = []
    for i, track in enumerate(tracks):
        role = track.get('role', 'narration')
        if role not in groups or not Path(track['path']).is_file():
            raise ValueError('Invalid audio role or missing local source')
        start = float(track.get('start', 0)); source_in = float(track.get('in', 0))
        gain = float(track.get('gain_db', 0)); length = float(track.get('duration', duration-start))
        if not all(math.isfinite(x) for x in (start, source_in, gain, length)) or min(start, source_in) < 0 or length <= 0 or start >= duration:
            raise ValueError('Invalid track placement or duration')
        command += ['-i', str(track['path'])]
        filters.append(f'[{i}:a]atrim=start={source_in}:duration={length},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,adelay={round(start*1000)}:all=1[placed{i}]')
        if role == 'music':
            duck=[]
            for voice in tracks:
                if voice.get('role') != 'narration': continue
                voice_start=float(voice.get('start',0)); voice_end=voice_start+float(voice.get('duration',duration-voice_start))
                attack=.25; release=.45; floor=.18
                duck.append(f"if(lt(t,{voice_start-attack:.6f}),1,if(lt(t,{voice_start:.6f}),1-(1-{floor})*(t-({voice_start-attack:.6f}))/{attack},if(lt(t,{voice_end:.6f}),{floor},if(lt(t,{voice_end+release:.6f}),{floor}+(1-{floor})*(t-{voice_end:.6f})/{release},1))))")
            if duck:
                expression=duck[0]
                for candidate in duck[1:]: expression=f'min({expression},{candidate})'
                filters.append(f"[placed{i}]volume='{expression}':eval=frame,apad=whole_dur={duration},atrim=duration={duration}[t{i}]")
            else:
                filters.append(f'[placed{i}]anull[t{i}]')
        else:
            filters.append(f'[placed{i}]anull[t{i}]')
        groups[role].append(f'[t{i}]')
    buses = {}
    for role, labels in groups.items():
        if labels:
            filters.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0,apad,atrim=duration={duration}[{role}]')
            buses[role] = f'[{role}]'
    filters.append(''.join(buses.values())+f'amix=inputs={len(buses)}:duration=longest:normalize=0,alimiter=limit=0.84:level=0,apad=whole_dur={duration},atrim=duration={duration}[out]')
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    command += ['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map','[out]',
                '-c:a','pcm_s16le','-ar','48000',str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    output.with_suffix('.mix.log').write_text(json.dumps(command)+'\n'+result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Audio mixing failed: '+result.stderr[-1500:])
    return str(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path); parser.add_argument('output', type=Path)
    parser.add_argument('--ffmpeg', required=True)
    args=parser.parse_args(); data=json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    for track in data['tracks']:
        track['path']=str((args.manifest.resolve().parent/track['path']).resolve())
    mix(data['tracks'], data['duration'], args.output, args.ffmpeg)
