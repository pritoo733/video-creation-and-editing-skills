"""Bounded, keyless Commons video search with explicit license evidence."""
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AGENT = 'VideoProductionSkills/1.0 (https://github.com/pritoo733/video-creation-and-editing-skills)'
API = 'https://commons.wikimedia.org/w/api.php'


def request(url):
    for attempt in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': AGENT}), timeout=45)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503) or attempt == 2:
                raise
            time.sleep(min(8, 2 ** attempt))


def clean(value):
    return html.unescape(re.sub('<[^>]+>', '', str(value))).strip()


def allowed_license(label, url):
    if re.search(r'non.?commercial|no.?deriv|by[ -]?(?:sa|nc|nd)|restricted|all rights', label, re.I):
        return False
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ''
    if host not in ('creativecommons.org', 'www.creativecommons.org') or parsed.scheme != 'https':
        return False
    return bool(re.fullmatch(r'/licenses/by/(?:2\.0|2\.5|3\.0|4\.0)/?', parsed.path)
                or re.fullmatch(r'/publicdomain/(?:zero|mark)/1\.0/?', parsed.path))


def normalize(page):
    info = (page.get('imageinfo') or [{}])[0]
    meta = info.get('extmetadata', {})
    get = lambda key: clean(meta.get(key, {}).get('value', ''))
    license_name, license_url = get('LicenseShortName'), get('LicenseUrl')
    # Commons sometimes omits a canonical license URL on public-domain files.
    if license_name.lower() in ('public domain', 'pd') and not license_url:
        license_url = 'https://creativecommons.org/publicdomain/mark/1.0/'
    url = info.get('url', '')
    if not allowed_license(license_name, license_url) or get('Restrictions'):
        return None
    if '/licenses/by/' in license_url and not get('Artist'):
        return None
    if urllib.parse.urlparse(url).hostname != 'upload.wikimedia.org':
        return None
    if not info.get('duration') or info.get('mime', '').split('/')[0] != 'video':
        return None
    return dict(id=str(page['pageid']), title=page['title'], url=url,
                page=info['descriptionurl'], width=info['width'], height=info['height'],
                duration=float(info['duration']), size=info.get('size', 0),
                author=get('Artist'), description=get('ImageDescription'),
                license=license_name, license_url=license_url, evidence=page)


def search(query, minimum_width=1280, minimum_height=720):
    if not isinstance(query, str) or not query.strip():
        raise ValueError('A shot-specific search query is required')
    candidates = []
    # Small bounded searches, not a library scrape. Keep metadata batches small.
    for offset in (0, 8, 16):
        params = dict(action='query', format='json', generator='search', gsrsearch=query+' filetype:video',
                      gsrnamespace=6, gsrlimit=8, gsroffset=offset, prop='imageinfo',
                      iiprop='url|size|mime|extmetadata', iiextmetadatalanguage='en')
        with request(API+'?'+urllib.parse.urlencode(params)) as response:
            data = json.load(response)
        if data.get('error'):
            raise RuntimeError('Commons API error: '+str(data['error']))
        pages = sorted(data.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 999))
        for page in pages:
            asset = normalize(page)
            if asset and asset['width'] >= minimum_width and asset['height'] >= minimum_height and asset['size'] <= 350_000_000:
                candidates.append(asset)
        if len(candidates) >= 4 or 'continue' not in data:
            break
    return candidates


def rank(candidates, query, duration, used):
    words = set(re.findall(r'[a-z]{3,}', query.lower()))
    def score(asset):
        terms = set(re.findall(r'[a-z]{3,}', (asset['title']+' '+asset['description']).lower()))
        return len(words & terms)*10 + min(asset['width'], 3840)/3840
    eligible = [a for a in candidates if a['id'] not in used and a['duration'] >= duration+.2]
    return sorted(eligible, key=score, reverse=True)


def download(asset, directory):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    suffix = Path(urllib.parse.urlparse(asset['url']).path).suffix
    target = directory/(asset['id']+suffix)
    if not target.exists():
        pending = target.with_suffix(target.suffix+'.part')
        try:
            with request(asset['url']) as response, pending.open('wb') as output:
                total = 0
                while chunk := response.read(1024*1024):
                    total += len(chunk)
                    if total > 350_000_000:
                        raise ValueError('Media exceeds the 350 MB per-file limit')
                    output.write(chunk)
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)
    evidence = directory/(asset['id']+'-license.json')
    evidence.write_text(json.dumps(asset['evidence'], indent=2), encoding='utf-8')
    asset = dict(asset, local_path=str(target), evidence_path=str(evidence),
                 sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                 checked_on=datetime.now(timezone.utc).date().isoformat())
    return asset


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query'); parser.add_argument('--min-width', type=int, default=1280)
    args = parser.parse_args()
    print(json.dumps([{k:v for k,v in a.items() if k!='evidence'} for a in search(args.query, args.min_width)], indent=2))
