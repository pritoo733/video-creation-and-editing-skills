"""Check the installed free runtime without rendering or purchasing anything."""
import argparse
import importlib
import json
from pathlib import Path
import subprocess
import sys


def doctor(config):
    for name in ('PIL','imageio_ffmpeg','piper','scenedetect','cv2','opentimelineio','imagehash','faster_whisper'):
        importlib.import_module(name)
    for path in (config['voice'],config['voice']+'.json',config['voice_card']):
        if not Path(path).is_file(): raise ValueError('Missing voice asset: '+path)
    result=subprocess.run([config['ffmpeg'],'-hide_banner','-filters'],capture_output=True,text=True,check=True)
    required=('subtitles','volume','amix','zoompan','crop','xfade')
    if not all(name in result.stdout for name in required):
        raise ValueError('FFmpeg lacks a required filter')
    subprocess.run([sys.executable,'-m','pip','check'],check=True)
    return dict(status='ready',paid_services=[],required_filters=list(required),voice=Path(config['voice']).name)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('runtime',type=Path)
    args=parser.parse_args()
    print(json.dumps(doctor(json.loads(args.runtime.read_text(encoding='utf-8-sig'))),indent=2))
