"""Check the installed free runtime without rendering or purchasing anything."""
import argparse
import importlib
import json
from pathlib import Path
import subprocess
import sys


def doctor(config):
    modules=['PIL','imageio_ffmpeg','scenedetect','cv2','opentimelineio','imagehash','faster_whisper']
    if config.get('tts_engine','piper')=='piper': modules.append('piper')
    elif config.get('tts_engine')=='pocket': modules.extend(('pocket_tts','scipy','numpy','torch'))
    else: raise ValueError('Unsupported tts_engine in runtime config')
    for name in modules:
        importlib.import_module(name)
    if config.get('tts_engine','piper')=='piper':
        for path in (config['voice'],config['voice']+'.json',config['voice_card']):
            if not Path(path).is_file(): raise ValueError('Missing voice asset: '+path)
    result=subprocess.run([config['ffmpeg'],'-hide_banner','-filters'],capture_output=True,text=True,check=True)
    required=('subtitles','volume','amix','zoompan','crop','xfade')
    if not all(name in result.stdout for name in required):
        raise ValueError('FFmpeg lacks a required filter')
    subprocess.run([sys.executable,'-m','pip','check'],check=True)
    voice=config.get('pocket_voice') if config.get('tts_engine')=='pocket' else Path(config['voice']).name
    return dict(status='ready',paid_services=[],required_filters=list(required),tts_engine=config.get('tts_engine','piper'),voice=voice)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('runtime',type=Path)
    args=parser.parse_args()
    print(json.dumps(doctor(json.loads(args.runtime.read_text(encoding='utf-8-sig'))),indent=2))
