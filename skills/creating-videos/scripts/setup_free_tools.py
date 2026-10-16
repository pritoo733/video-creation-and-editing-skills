"""Install a local, no-paid-service production runtime and a public-domain-data voice."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv
from free_media import request

VOICE_ROOT = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ljspeech/high/'


def setup(destination, reuse_voice=None):
    destination = Path(destination).resolve()
    python = destination/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if not python.exists():
        venv.create(destination, with_pip=True)
    requirements = Path(__file__).resolve().parents[1]/'assets/free-requirements.txt'
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(requirements)], check=True)
    models = destination/'models'; models.mkdir(exist_ok=True)
    voice = models/'en_US-ljspeech-high.onnx'
    if reuse_voice and Path(reuse_voice).name != voice.name:
        raise ValueError('The reusable free default must be en_US-ljspeech-high; review other voice terms separately')
    for name in (voice.name, voice.name+'.json', 'MODEL_CARD'):
        target = models/name
        if target.exists():
            continue
        if reuse_voice and name != 'MODEL_CARD':
            origin = Path(str(reuse_voice)+('.json' if name.endswith('.json') else ''))
            shutil.copy2(origin, target)
        else:
            with request(VOICE_ROOT+name) as response, target.with_suffix(target.suffix+'.part').open('wb') as out:
                shutil.copyfileobj(response, out)
            target.with_suffix(target.suffix+'.part').replace(target)
    code = 'import imageio_ffmpeg,json,importlib.metadata as m; print(json.dumps(dict(ffmpeg=imageio_ffmpeg.get_ffmpeg_exe(),packages={p:m.version(p) for p in '+repr(['Pillow','imageio-ffmpeg','piper-tts','scenedetect','opencv-python-headless','opentimelineio','ImageHash','faster-whisper'])+'})))'
    details = json.loads(subprocess.run([str(python), '-c', code], capture_output=True, text=True, check=True).stdout)
    config = dict(details, python=str(python), voice=str(voice), voice_card=str(models/'MODEL_CARD'),
                  voice_source=VOICE_ROOT, voice_dataset='https://keithito.com/LJ-Speech-Dataset/',
                  network_services=['Wikimedia Commons API', 'PyPI and Hugging Face for setup'], paid_services=[])
    (destination/'runtime.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    print(json.dumps(config, indent=2))
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, required=True)
    parser.add_argument('--reuse-voice', type=Path, help='Existing en_US-ljspeech-high model; its matching .json is required')
    args = parser.parse_args()
    setup(args.dest, args.reuse_voice)
