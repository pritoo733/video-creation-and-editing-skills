"""List 21 hook categories or audit an agent-authored script package; Python stdlib only."""
import argparse
import json
import math
from pathlib import Path
import re

CATALOG = Path(__file__).resolve().parents[1] / 'assets/hook-formulas.json'


def words(text):
    return re.findall(r"\w+(?:['’-]\w+)*", str(text).casefold())


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def review(plan, base=Path('.')):
    if not isinstance(plan, dict):
        raise ValueError('Script package must be a JSON object')
    formulas = {item['id']: item for item in json.loads(CATALOG.read_text(encoding='utf-8'))['hooks']}
    errors, warnings, panels = [], [], []
    for field in ('audience', 'viewer_promise', 'title'):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            errors.append(f'Missing {field}')
    wpm = plan.get('spoken_wpm', 150)
    window = plan.get('hook_window_seconds', 15)
    if not number(wpm) or wpm <= 0 or not number(window) or window <= 0:
        raise ValueError('spoken_wpm and hook_window_seconds must be positive finite numbers')
    beats = plan.get('beats', [])
    candidates = plan.get('hooks', [])
    sources = plan.get('sources', {})
    if not isinstance(beats, list) or not isinstance(candidates, list) or not isinstance(sources, dict):
        raise ValueError('beats/hooks must be arrays and sources must be an object')
    if not beats: errors.append('No script beats')
    if not candidates: errors.append('No hook candidates')
    beat_map, cursor, spoken_words = {}, 0, 0
    for beat in beats:
        if not isinstance(beat, dict):
            errors.append('Each beat must be an object'); continue
        ident = beat.get('id')
        if not isinstance(ident, str) or not ident or ident in beat_map:
            errors.append('Beat IDs must be nonempty unique strings'); continue
        beat_map[ident] = beat
        start, end = beat.get('start'), beat.get('end')
        if not number(start) or not number(end) or end <= start or abs(start - cursor) > 1e-6:
            errors.append(f'{ident}: beats must cover contiguous positive time intervals from zero')
        else:
            cursor = end
            if len(words(beat.get('narration', ''))) * 60 / wpm > end - start:
                warnings.append(f'{ident}: estimated narration exceeds this beat; measure speech and retime')
        if not str(beat.get('visual_action', '')).strip(): errors.append(f'{ident}: missing visible action')
        spoken_words += len(words(beat.get('narration', '')))
    if 'duration' in plan and (not number(plan['duration']) or abs(plan['duration'] - cursor) > 1e-6):
        errors.append('Beat timing does not match duration')
    ids, normalized_texts = set(), set()
    selected = plan.get('selected_hook_id')
    selected_hook = None
    for hook in candidates:
        if not isinstance(hook, dict): errors.append('Each hook must be an object'); continue
        issues, hints = [], []
        ident, formula_id = hook.get('id'), hook.get('formula_id')
        if not isinstance(ident, str) or not ident or ident in ids:
            issues.append('Hook IDs must be nonempty unique strings')
        else: ids.add(ident)
        formula = formulas.get(formula_id) if isinstance(formula_id, str) else None
        if not formula: issues.append('Unknown formula_id')
        text = hook.get('text', '')
        if not isinstance(text, str): text = ''; issues.append('Hook text must be a string')
        tokens = words(text)
        normalized = ' '.join(tokens)
        if not tokens: issues.append('Empty hook')
        elif normalized in normalized_texts: issues.append('Duplicate opening text')
        normalized_texts.add(normalized)
        estimate = len(tokens) * 60 / wpm
        if estimate > window: hints.append('Estimated speech exceeds hook window; shorten or retime and audition')
        if not str(hook.get('opening_visual', '')).strip(): issues.append('Missing opening visual')
        payoff = hook.get('payoff_beat_id')
        if not isinstance(payoff, str) or payoff not in beat_map: issues.append('Payoff must reference an existing beat')
        elif not str(beat_map[payoff].get('delivers', '')).strip(): issues.append('Payoff beat needs an explicit delivers statement')
        evidence = hook.get('evidence_ids', [])
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            issues.append('evidence_ids must be an array of source IDs'); evidence = []
        if formula and formula['proof_required'] and not evidence:
            issues.append('This formula requires a reviewed evidence record')
        for source_id in evidence:
            source = sources.get(source_id)
            if not isinstance(source, dict) or source.get('reviewed') is not True:
                issues.append(f'{source_id}: missing or unreviewed source'); continue
            if source.get('path'):
                if not isinstance(source['path'], str) or not (base / source['path']).is_file(): issues.append(f'{source_id}: local evidence file missing')
            elif not isinstance(source.get('url'), str) or not source['url'].startswith(('https://', 'http://')):
                issues.append(f'{source_id}: provide a local path or source URL')
        if re.search(r'\d', text) and not evidence: hints.append('Numeric wording needs a source or an explicit body-count/timing check')
        if re.search(r'\b(best|guaranteed|fastest|everyone|nobody|always|never)\b', text, re.I): hints.append('Review absolute/superlative wording against the actual evidence')
        panels.append(dict(id=ident, formula_id=formula_id, word_count=len(tokens), estimated_seconds=round(estimate, 2), errors=issues, warnings=hints))
        if ident == selected:
            selected_hook = hook
            errors.extend(f'{ident}: {issue}' for issue in issues)
    if selected_hook is None:
        errors.append('selected_hook_id must identify a candidate')
    elif beats and isinstance(beats[0], dict) and not ' '.join(words(beats[0].get('narration', ''))).startswith(' '.join(words(selected_hook.get('text', '')))):
        errors.append('Opening beat does not begin with the selected hook; reconcile the script and choice')
    for panel in panels:
        if panel['errors'] and panel['id'] != selected: warnings.append(f"Rejected candidate {panel['id']} has unresolved issues")
    if len(panels) < 2: warnings.append('Only one opening considered; compare alternatives when useful')
    if len({p['formula_id'] for p in panels if isinstance(p['formula_id'], str)}) < min(3, len(panels)):
        warnings.append('Try a different opening approach rather than only rewording the same formula')
    title_words = set(words(plan.get('title', '')))
    thumb_words = set(words(plan.get('thumbnail_text', '')))
    if thumb_words and len(title_words & thumb_words) / len(thumb_words) >= .75:
        warnings.append('Thumbnail repeats much of the title; review whether image and copy add meaning')
    if len(str(plan.get('title', ''))) > 70: warnings.append('Long title: inspect real destination rendering and front-load the subject')
    if spoken_words * 60 / wpm > cursor: warnings.append('Estimated narration exceeds planned runtime; measure real audio before final timing')
    return dict(status='needs_revision' if errors else 'editorial_review_required', errors=errors, warnings=warnings,
                hooks=panels, estimated_script_seconds=round(spoken_words * 60 / wpm, 2), planned_seconds=cursor,
                review_scope='Structural and wording checks only. Source flags are declarations, not proof of truth. No view/retention prediction.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', nargs='?', type=Path)
    parser.add_argument('--list', action='store_true', help='Print the complete hook catalog as JSON')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.list:
            result = json.loads(CATALOG.read_text(encoding='utf-8'))
        elif args.plan:
            result = review(json.loads(args.plan.read_text(encoding='utf-8')), args.plan.resolve().parent)
        else: parser.error('Provide a script package or --list')
        text = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text + '\n', encoding='utf-8')
        else: print(text)
        return int(result.get('status') == 'needs_revision')
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, f'{exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
