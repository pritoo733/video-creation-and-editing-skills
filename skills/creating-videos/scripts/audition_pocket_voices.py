"""Create a local, clickable audition page for Pocket TTS English presets."""
import argparse
import html
import json
from pathlib import Path

from setup_free_tools import POCKET_VOICES, POCKET_LICENSES, POCKET_MODEL


SAMPLE_TEXT = (
    "Hi, and welcome. In this video, we will show you how real estate lenders can "
    "keep deals moving with a clearer process."
)


def build_audition(output):
    try:
        import numpy as np
        import torch
        from pocket_tts import TTSModel
        from scipy.io import wavfile
    except ImportError as exc:
        raise RuntimeError(
            "Pocket TTS dependencies are missing. Install the runtime with "
            "setup_free_tools.py --tts-engine pocket first."
        ) from exc

    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    model = TTSModel.load_model()
    records = []
    for voice, (source, license_name, creator) in POCKET_VOICES.items():
        print(f"Generating {voice} sample", flush=True)
        voice_state = model.get_state_for_audio_prompt(voice)
        with torch.inference_mode():
            samples = model.generate_audio(voice_state, SAMPLE_TEXT).detach().cpu().numpy()
        audio_path = output / f"{voice}.wav"
        wavfile.write(str(audio_path), model.sample_rate,
                      (np.clip(samples, -1, 1) * 32767).astype(np.int16))
        records.append({
            "voice": voice,
            "sample": audio_path.name,
            "source": source,
            "license": license_name,
            "creator": creator,
            "source_url": f"{POCKET_LICENSES}/{source}",
            "model_url": POCKET_MODEL,
        })

    (output / "voice-auditions.json").write_text(
        json.dumps({"sample_text": SAMPLE_TEXT, "voices": records}, indent=2),
        encoding="utf-8",
    )
    cards = []
    for item in records:
        warning = " <strong>Noncommercial only.</strong>" if "NC" in item["license"] else ""
        cards.append(f"""
        <article class="voice-card">
          <label><input type="radio" name="voice" value="{html.escape(item['voice'])}">
            <span class="voice-name">{html.escape(item['voice'])}</span></label>
          <audio controls preload="none" src="{html.escape(item['sample'])}"></audio>
          <p>{html.escape(item['creator'])} · {html.escape(item['license'])}.{warning}</p>
          <a href="{html.escape(item['source_url'])}" target="_blank" rel="noopener">Voice source and license</a>
        </article>""")
    page = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choose your voiceover voice</title>
<style>
body{{font:16px/1.5 system-ui,sans-serif;margin:0;background:#f4f6fa;color:#172033}}
main{{max-width:1050px;margin:40px auto;padding:0 20px}}h1{{font-size:2rem}}.notice{{background:#fff4d7;padding:14px 18px;border-radius:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}.voice-card{{background:white;border:1px solid #dce2eb;border-radius:14px;padding:16px}}
.voice-card audio{{display:block;width:100%;margin:12px 0}}.voice-name{{font-size:1.1rem;font-weight:700}}.actions{{position:sticky;bottom:0;background:#172033;color:white;padding:14px;border-radius:12px;margin:18px 0}}
button{{padding:10px 14px;font-weight:700;cursor:pointer}}a{{color:#1757a6}}
</style><main><h1>Choose your English voiceover</h1>
<p>Listen to the same short line in all {len(records)} Pocket TTS English presets, then select the voice you want. English is the listed language; the upstream catalog does not certify gender or regional accent, so choose by listening.</p>
<p class="notice">Voice licenses differ. The Expresso and EARS presets marked CC BY-NC are noncommercial only. Review the source and license before using a voice in a commercial or monetized video. <a href="{POCKET_LICENSES}" target="_blank" rel="noopener">Official voice catalog</a></p>
<p><strong>Sample line:</strong> {html.escape(SAMPLE_TEXT)}</p><section class="grid">{''.join(cards)}</section>
<div class="actions"><span id="choice">Choose a voice above.</span> <button id="save" disabled>Download voice selection</button></div>
</main><script>
const radios=[...document.querySelectorAll('input[name=voice]')], label=document.querySelector('#choice'), save=document.querySelector('#save');
let selected=''; radios.forEach(r=>r.addEventListener('change',()=>{{selected=r.value;label.textContent='Selected voice: '+selected;save.disabled=false;}}));
save.addEventListener('click',()=>{{const blob=new Blob([JSON.stringify({{voice:selected,sample_text:{json.dumps(SAMPLE_TEXT)}}},null,2)],{{type:'application/json'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='voice-selection.json';a.click();URL.revokeObjectURL(a.href);}});
</script></html>"""
    (output / "index.html").write_text(page, encoding="utf-8")
    print(f"Open {output / 'index.html'} and listen to all {len(records)} samples.")
    return output / "index.html"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="Project-local folder for the 21 audio previews and audition page")
    args = parser.parse_args()
    build_audition(args.output)
