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
POCKET_VOICES = {
    'alba': ('alba-mackenna/casual.wav', 'CC BY 4.0', 'Alba MacKenna'),
    'anna': ('vctk/p228_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'azelma': ('vctk/p303_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'bill_boerst': ('voice-zero/bill_boerst.wav', 'CC0', 'Voice-Zero'),
    'caro_davy': ('voice-zero/caro_davy.wav', 'CC0', 'Voice-Zero'),
    'charles': ('vctk/p254_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'cosette': ('expresso/ex04-ex02_confused_001_channel1_499s.wav', 'CC BY-NC 4.0', 'Expresso'),
    'eponine': ('vctk/p262_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'eve': ('vctk/p361_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'fantine': ('vctk/p244_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'george': ('vctk/p315_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'jane': ('vctk/p339_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'jean': ('ears/p010/freeform_speech_01_enhanced.wav', 'CC BY-NC 4.0', 'EARS'),
    'javert': ('voice-donations/Butter.wav', 'CC0', 'Unmute Voice Donation Project'),
    'marius': ('voice-donations/Selfie.wav', 'CC0', 'Unmute Voice Donation Project'),
    'mary': ('vctk/p333_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'michael': ('vctk/p360_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'paul': ('vctk/p259_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
    'peter_yearsley': ('voice-zero/peter_yearsley.wav', 'CC0', 'Voice-Zero'),
    'stuart_bell': ('voice-zero/stuart_bell.wav', 'CC0', 'Voice-Zero'),
    'vera': ('vctk/p229_023_enhanced.wav', 'CC BY 4.0', 'VCTK'),
}
POCKET_LICENSES = 'https://huggingface.co/kyutai/tts-voices'
POCKET_MODEL = 'https://huggingface.co/kyutai/pocket-tts'


def setup(destination, reuse_voice=None, tts_engine='pocket', pocket_voice='alba'):
    if tts_engine not in ('piper', 'pocket'):
        raise ValueError('tts_engine must be piper or pocket')
    if pocket_voice not in POCKET_VOICES:
        raise ValueError(f'Unknown Pocket TTS voice: {pocket_voice}')
    destination = Path(destination).resolve()
    python = destination/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if not python.exists():
        venv.create(destination, with_pip=True)
    requirements = Path(__file__).resolve().parents[1]/'assets/free-requirements.txt'
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(requirements)], check=True)
    if tts_engine == 'pocket':
        subprocess.run([str(python), '-m', 'pip', 'install', 'pocket-tts'], check=True)
    models = destination/'models'; models.mkdir(exist_ok=True)
    voice = models/'en_US-ljspeech-high.onnx'
    if reuse_voice and Path(reuse_voice).name != voice.name:
        raise ValueError('The reusable free default must be en_US-ljspeech-high; review other voice terms separately')
    if tts_engine == 'piper':
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
    package_info=json.loads(subprocess.run([str(python), '-c', code], capture_output=True, text=True, check=True).stdout)
    if tts_engine == 'pocket':
        package_info['packages']['pocket-tts']=importlib.metadata.version('pocket-tts')
    details=package_info
    voice_info = POCKET_VOICES[pocket_voice]
    config = dict(details, python=str(python), tts_engine=tts_engine,
                  pocket_voice=pocket_voice, pocket_voice_source=voice_info[0],
                  pocket_voice_license=voice_info[1], pocket_voice_creator=voice_info[2],
                  pocket_voice_catalog=POCKET_LICENSES, pocket_model=POCKET_MODEL,
                  voice=str(voice), voice_card=str(models/'MODEL_CARD'),
                  voice_source=VOICE_ROOT, voice_dataset='https://keithito.com/LJ-Speech-Dataset/',
                  network_services=['Wikimedia Commons API', 'PyPI and Hugging Face for setup'], paid_services=[])
    (destination/'runtime.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    print(json.dumps(config, indent=2))
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, required=True)
    parser.add_argument('--reuse-voice', type=Path, help='Existing en_US-ljspeech-high model; its matching .json is required')
    parser.add_argument('--tts-engine', choices=('piper', 'pocket'), default='pocket',
                        help='Local speech backend; Pocket TTS is the default and downloads its model on first use')
    parser.add_argument('--pocket-voice', choices=tuple(POCKET_VOICES), default='alba',
                        help='Pocket TTS voice preset; check its dataset license before publishing')
    args = parser.parse_args()
    setup(args.dest, args.reuse_voice, args.tts_engine, args.pocket_voice)
