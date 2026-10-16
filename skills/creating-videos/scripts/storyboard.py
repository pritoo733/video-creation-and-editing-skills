"""Write a portable, local storyboard for review before the full video render."""
import base64
import html
import json
from pathlib import Path


def write_storyboard(plan, shots, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    beats = {f'beat-{i+1:02}': beat for i, beat in enumerate(plan['beats'])}
    cards = []
    for shot in shots:
        preview_path = Path(shot['preview_path'])
        if not preview_path.is_file():
            raise ValueError(f'Missing storyboard preview for {shot["visual_id"]}: {preview_path}')
        image = base64.b64encode(preview_path.read_bytes()).decode('ascii')
        beat = beats[shot['beat_id']]
        rights = shot.get('rights', {})
        source_title = shot.get('asset_title', 'Original animated graphic')
        source_link = rights.get('source_url', '')
        license_link = rights.get('license_url', '')
        license_name = shot.get('asset_license') or rights.get('license')
        if not license_name and license_link:
            license_name = 'Public domain' if '/publicdomain/' in license_link else 'CC BY' if '/licenses/by/' in license_link else 'Review required'
        license_name = license_name or 'Original graphic'
        cards.append(dict(visual_id=shot['visual_id'], beat_id=shot['beat_id'],
                          narration=beat['narration'], seconds=shot['duration'],
                          action=shot.get('visual_action', ''), why_it_fits=shot['why_it_fits'],
                          source_title=source_title, source_url=source_link,
                          license=license_name, license_url=license_link,
                          preview_path=str(preview_path.resolve()), image_data=image))
    (output/'storyboard.json').write_text(json.dumps(dict(title=plan.get('title', 'Production storyboard'),
        brief=plan['brief'], cards=cards), indent=2), encoding='utf-8')
    esc = lambda value: html.escape(str(value), quote=True)
    sections = []
    for i, card in enumerate(cards, 1):
        source = f'<a href="{esc(card["source_url"])}">{esc(card["source_title"])}</a>' if card['source_url'] else esc(card['source_title'])
        license_info = esc(card['license'])
        if card['license_url']:
            license_info += f' · <a href="{esc(card["license_url"])}">license</a>'
        sections.append(f'''<article class="card">
          <img src="data:image/jpeg;base64,{card['image_data']}" alt="Preview for {esc(card['visual_id'])}">
          <div class="meta"><span>{i:02} · {esc(card['visual_id'])}</span><span>{card['seconds']:.2f}s</span></div>
          <h2>{esc(card['action'])}</h2>
          <p class="script">“{esc(card['narration'])}”</p>
          <p><b>Why this shot:</b> {esc(card['why_it_fits'])}</p>
          <p><b>Source:</b> {source}</p><p><b>Rights:</b> {license_info}</p>
        </article>''')
    title = esc(plan.get('title', 'Production storyboard'))
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Storyboard</title><style>
:root{{--ink:#142533;--muted:#596b79;--paper:#f4f6f7;--card:#fff;--accent:#176c62;--line:#dae2e5}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
header{{padding:34px clamp(20px,5vw,76px);background:#10212d;color:#f5f8f8}}header small{{color:#8ed9ca;text-transform:uppercase;letter-spacing:.12em;font-weight:700}}
h1{{margin:.4rem 0;font-size:clamp(28px,4vw,46px);line-height:1.1}}header p{{max-width:980px;color:#c2d0d4;margin:.7rem 0 0}}
.notice{{margin:24px clamp(20px,5vw,76px);padding:14px 18px;border-left:4px solid #d99538;background:#fff8e9;color:#453618}}
main{{padding:0 clamp(20px,5vw,76px) 56px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:22px}}
.card{{overflow:hidden;border:1px solid var(--line);border-radius:15px;background:var(--card);box-shadow:0 8px 24px #10212d0b}}
.card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#d9e1e4}}.card>p,.card h2,.meta{{margin-left:20px;margin-right:20px}}
.meta{{display:flex;justify-content:space-between;margin-top:17px;color:var(--accent);font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.055em}}
h2{{font-size:22px;line-height:1.25;margin-top:9px;margin-bottom:12px}}p{{color:var(--muted)}}.script{{padding:12px 14px;background:#eef5f3;border-radius:9px;color:#1c3938;font-size:17px}}
a{{color:#075d80;overflow-wrap:anywhere}}footer{{padding:20px clamp(20px,5vw,76px);border-top:1px solid var(--line);color:var(--muted);font-size:14px}}
</style></head><body><header><small>Free local production · pre-render board</small><h1>{title}</h1><p>{esc(plan['brief'])}</p></header>
<div class="notice"><b>Draft review:</b> Check each image against the spoken line, confirm credits and source terms, and revise the plan if a shot is weak. This board is not the rendered video.</div>
<main>{''.join(sections)}</main><footer>Generated by the free local workflow. Preview images are embedded in this file; source links require an internet connection. Keep the accompanying storyboard.json and project assets for revisions.</footer></body></html>'''
    path = output/'storyboard.html'
    path.write_text(document, encoding='utf-8')
    return str(path)
