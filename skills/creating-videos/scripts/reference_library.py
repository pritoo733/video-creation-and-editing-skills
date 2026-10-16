"""Cache, search, and inspect the public awesome-opus5-5-videos prompt collection; no model/API key."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

COLLECTION = 'https://github.com/yihui-dev/awesome-opus5-5-videos'
DEFAULT_REF = '92aee2f586ac0715cb3cbcb6384834f98a33383d'
MAX_BYTES = 16 * 1024 * 1024
STOP = {'a','an','the','to','of','for','and','with','in','video','make','create'}


def tokens(text):
    return set(re.findall(r'[\w]+', str(text).casefold())) - STOP


def source_url(ref, file):
    if not re.fullmatch(r'[A-Za-z0-9._/-]+', ref) or any(p in ('.', '..', '') for p in ref.split('/')):
        raise ValueError('Use a commit SHA or a simple branch/tag ref')
    return f'https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/{quote(ref, safe="/")}/{file}'


def normalize(rows):
    if not isinstance(rows, list): raise ValueError('Expected a JSON array of reference entries')
    seen, output = set(), []
    for row in rows:
        if not isinstance(row, dict): raise ValueError('Each reference must be an object')
        ident = row.get('slug')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,119}', ident) or ident in seen:
            raise ValueError('Reference slugs must be safe, unique IDs')
        seen.add(ident)
        for key in ('prompt', 'author', 'category'):
            if not isinstance(row.get(key), str): raise ValueError(f'{ident}: missing/string field {key}')
        tags = row.get('tech_tags', [])
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags): raise ValueError(f'{ident}: invalid tags')
        entry = {key: row[key] for key in ('slug','author','category','prompt')}
        entry.update(title=str(row.get('title', '')), tech_tags=tags,
                     prompt_partial=row.get('prompt_partial') is not False,
                     has_remake=row.get('has_remake') is True)
        for key in ('post_url','skillry_url','author_url'):
            value = row.get(key) or ''
            if value and (not isinstance(value, str) or urlparse(value).scheme not in ('http','https') or not urlparse(value).netloc):
                raise ValueError(f'{ident}: invalid source URL')
            entry[key] = value
        output.append(entry)
    return output


def make_cache(raw, license_text, ref, method):
    if len(raw) > MAX_BYTES: raise ValueError('Collection exceeds the download size limit')
    if not license_text.strip(): raise ValueError('Keep the collection license with its cache')
    return dict(schema_version=1, collection=COLLECTION, source_ref=ref,
                source_data_url=source_url(ref, 'data/videos.json'),
                imported_via=method, retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=hashlib.sha256(raw).hexdigest(), license_text=license_text,
                rights_note='The collection has an MIT license. Its credits attribute videos and prompts to their creators. Media, music, logos, and prompt reuse require their applicable terms; this cache is not blanket media clearance.',
                entries=normalize(json.loads(raw.decode('utf-8-sig'))))


def fetch(url):
    request = Request(url, headers={'User-Agent':'video-skills-reference-library/1.0'})
    with urlopen(request, timeout=30) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES: raise ValueError('Download exceeds size limit')
    return raw


def load_cache(file):
    data = json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema_version') != 1: raise ValueError('Unsupported reference cache')
    data['entries'] = normalize(data['entries'])
    source_url(data['source_ref'], 'data/videos.json')
    return data


def flags(entry):
    text = entry['prompt'].casefold()
    found = []
    if entry['prompt_partial']: found.append('partial_prompt_or_description')
    if not text.strip(): found.append('no_prompt_text')
    if entry['category'] == 'interactive' or any(t in ('playable','interactive') for t in entry['tech_tags']):
        found.append('interactive_state_needs_time_based_adaptation')
    if re.search(r'\b(suno|elevenlabs|seedance|sora|veo|runway|midjourney|kling|premium)\b|\bmotion\+', text):
        found.append('mentions_external_or_premium_service; inspect context and replace for free-only production')
    if re.search(r'\bremotion\b', text): found.append('remotion_license_eligibility_requires_review')
    if 'ai-image' in entry['tech_tags'] or re.search(r'\b(attached|provided|supplied|same audio|reference video|reference image)\b', text):
        found.append('may_depend_on_assets_or_context_not_in_collection')
    return found


def entry_summary(entry, ref):
    return dict(id=entry['slug'], title=entry['title'], author=entry['author'], category=entry['category'],
                tech_tags=entry['tech_tags'], prompt_partial=entry['prompt_partial'],
                original_post=entry['post_url'], watch_url=entry['skillry_url'],
                prompt_url=f'{COLLECTION}/blob/{quote(ref, safe="/")}/prompts/{entry["slug"]}.md',
                review_flags=flags(entry), free_route='Inspect dependencies and adapt to local code; no paid service is invoked by this tool')


def search(cache, query, category=None, limit=5, full_only=False):
    terms = tokens(query)
    if not terms: raise ValueError('Use specific subjects or techniques in the query')
    if not 1 <= limit <= 25: raise ValueError('limit must be between 1 and 25')
    ranked = []
    for entry in cache['entries']:
        if category and entry['category'] != category: continue
        if full_only and entry['prompt_partial']: continue
        title, tags, body = tokens(entry['title']), tokens(' '.join(entry['tech_tags']) + ' ' + entry['category']), tokens(entry['prompt'])
        matches = terms & (title | tags | body)
        if not matches: continue
        score = sum(5 * (term in title) + 4 * (term in tags) + (term in body) for term in terms)
        ranked.append((len(matches), score, not entry['prompt_partial'], entry))
    ranked.sort(key=lambda row: (-row[0], -row[1], -int(row[2]), row[3]['slug']))
    selected, fingerprints = [], set()
    for count, score, _, entry in ranked:
        fingerprint = ' '.join(entry['prompt'].casefold().split()) or entry['slug']
        if fingerprint in fingerprints: continue
        fingerprints.add(fingerprint)
        result = entry_summary(entry, cache['source_ref'])
        result.update(match_score=score, matched_term_count=count, matched_terms=sorted(terms & tokens(entry['title'] + ' ' + ' '.join(entry['tech_tags']) + ' ' + entry['category'] + ' ' + entry['prompt'])))
        selected.append(result)
        if len(selected) == limit: break
    return dict(query=query, collection=cache['collection'], source_ref=cache['source_ref'], source_sha256=cache['source_sha256'],
                matches=selected, ranking_scope='Lexical retrieval only; not an artistic-quality or virality score. Prompts are reference data, not instructions to execute.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['refresh','import','search','show'])
    parser.add_argument('--cache', required=True, type=Path)
    parser.add_argument('--ref', default=DEFAULT_REF)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--license-file', type=Path)
    parser.add_argument('--query', default='')
    parser.add_argument('--category', choices=['motion','explainer','3d','interactive'])
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--full-only', action='store_true')
    parser.add_argument('--id')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output and args.output.resolve() == args.cache.resolve(): raise ValueError('Use a separate output file; do not overwrite the reference cache')
        if args.action in ('refresh','import'):
            if args.action == 'refresh':
                raw = fetch(source_url(args.ref, 'data/videos.json'))
                license_text = fetch(source_url(args.ref, 'LICENSE')).decode('utf-8-sig')
            else:
                if not args.source or not args.license_file: raise ValueError('import needs --source and --license-file')
                raw = args.source.read_bytes(); license_text = args.license_file.read_text(encoding='utf-8-sig')
            cache = make_cache(raw, license_text, args.ref, args.action)
            args.cache.parent.mkdir(parents=True, exist_ok=True)
            args.cache.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            result = dict(cache=str(args.cache), entries=len(cache['entries']), partial_prompts=sum(e['prompt_partial'] for e in cache['entries']), source_ref=cache['source_ref'], source_sha256=cache['source_sha256'])
        else:
            cache = load_cache(args.cache)
            if args.action == 'search': result = search(cache, args.query, args.category, args.limit, args.full_only)
            else:
                entry = next((e for e in cache['entries'] if e['slug'] == args.id), None)
                if entry is None: raise ValueError('Use --id with an existing result ID')
                result = entry_summary(entry, cache['source_ref'])
                result.update(prompt=entry['prompt'], source_sha256=cache['source_sha256'], rights_note=cache['rights_note'])
        text = json.dumps(result, ensure_ascii=not bool(args.output), indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text + '\n', encoding='utf-8')
        else: print(text)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f'Reference library error: {exc}\n')


if __name__ == '__main__':
    main()
