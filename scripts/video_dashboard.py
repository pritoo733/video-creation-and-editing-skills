"""Serve a private, read-only dashboard for local video-production folders."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse
import webbrowser


REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / 'dashboard'
SKIP_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.video-tools', 'working', 'renders', 'cache', 'assets', 'source-media'}
MARKERS = {'plan.json', 'production-log.json', 'timeline.json'}
ARTIFACTS = {
    'final.mp4', 'storyboard.html', 'storyboard.json', 'CREDITS.md', 'captions.srt',
    'captions.ass', 'captions.json', 'review.json', 'review-contact-sheet.jpg', 'plan.json',
    'timeline.json', 'shots.json', 'asset-ledger.json', 'transcript.json', 'speech-check.json', 'google-flow-assets.json',
}


def read_json(path: Path) -> dict | list | None:
    try:
        value = json.loads(path.read_text(encoding='utf-8-sig'))
        return value if isinstance(value, (dict, list)) else None
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def is_safe_file(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=True).relative_to(root)
        return path.is_file()
    except (OSError, ValueError):
        return False


def _log_info(entries: list) -> tuple[str | None, dict[str, str]]:
    failed = False
    stage_status: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        stage = entry.get('stage')
        status = entry.get('status')
        if isinstance(stage, str) and isinstance(status, str):
            stage_status[stage] = status
            failed = failed or stage == 'production_failed' or status == 'failed'
    return ('failed' if failed else None), stage_status


def _milestone(name: str, complete: bool | None) -> dict:
    return {'name': name, 'state': 'complete' if complete is True else 'missing' if complete is False else 'unknown'}


def _voice_info(credits_path: Path) -> dict:
    try:
        text = credits_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return {'provider': None, 'voice': None}
    provider = voice = None
    match = re.search(r'Voice synthesis:\s*([^;\n]+)', text, re.IGNORECASE)
    if match:
        provider = match.group(1).strip()
    match = re.search(r'voice ID\s+([^;\s]+)', text, re.IGNORECASE)
    if match:
        voice = match.group(1)
    match = re.search(r'Voice preset:\s*([^;\n]+)', text, re.IGNORECASE)
    if match:
        voice = match.group(1).strip()
    match = re.search(r'^Voice:\s*([^;\n]+)', text, re.IGNORECASE | re.MULTILINE)
    if match and not provider:
        provider = match.group(1).strip()
    return {'provider': provider, 'voice': voice}


def _source_info(storyboard: dict | None, ledger: dict | None) -> list[dict]:
    cards = storyboard.get('cards', []) if isinstance(storyboard, dict) else []
    sources = []
    seen = set()
    for card in cards:
        if not isinstance(card, dict) or not card.get('source_url'):
            continue
        key = (card.get('source_url'), card.get('license_url'))
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            'title': str(card.get('source_title') or 'Source clip')[:180],
            'url': str(card.get('source_url'))[:1000],
            'license': str(card.get('license') or 'License not recorded')[:120],
            'license_url': str(card.get('license_url') or '')[:1000],
        })
    stock = ledger.get('stock', []) if isinstance(ledger, dict) else []
    if isinstance(stock, list):
        for item in stock:
            if not isinstance(item, dict) or not item.get('page'):
                continue
            key = (item.get('page'), item.get('license_url'))
            if key in seen:
                continue
            seen.add(key)
            sources.append({
                'title': str(item.get('title') or item.get('id') or 'Source clip')[:180],
                'url': str(item.get('page'))[:1000],
                'license': str(item.get('license_status') or 'License not recorded')[:120],
                'license_url': str(item.get('license_url') or '')[:1000],
            })
    return sources


def _deliverable_videos(folder: Path, root: Path) -> list[Path]:
    videos = []
    for path in folder.iterdir():
        if path.suffix.lower() != '.mp4' or not is_safe_file(path, root):
            continue
        stem = path.stem.lower()
        if stem.startswith('visuals') or re.search(r'(^|[-_])pilot([-_]|$)', stem) or stem == 'original-vs-revised':
            continue
        if path.stat().st_size:
            videos.append(path)
    return sorted(videos, key=lambda path: (path.stat().st_mtime, path.name.casefold()), reverse=True)


def _video_review(folder: Path, candidates: list[Path], video: Path) -> dict:
    reports = []
    for path in folder.iterdir():
        if path.suffix.lower() != '.json' or 'review' not in path.stem.lower():
            continue
        if not is_safe_file(path, folder.resolve()):
            continue
        report = read_json(path)
        if isinstance(report, dict):
            reports.append((path.stem.lower(), report))
    for _, report in reports:
        named = report.get('file')
        if not isinstance(named, str):
            validated = report.get('validated_artifact')
            named = validated.get('filename') if isinstance(validated, dict) else None
        if named and (Path(named).name == video.name):
            return report
    if len(candidates) == 1 and reports:
        return reports[0][1]
    video_stem = video.stem.lower()
    for report_name, report in reports:
        tag_v2 = 'v2' in report_name
        if tag_v2 == ('v2' in video_stem):
            return report
    return {}


def _video_metadata(report: dict, timeline: dict | None, use_timeline: bool) -> dict:
    meta = report.get('metadata', {}) if isinstance(report, dict) else {}
    if not isinstance(meta, dict):
        meta = {}
    streams = meta.get('streams', report.get('streams', {}) if isinstance(report, dict) else {})
    if isinstance(streams, list):
        streams = next((item for item in streams if isinstance(item, dict) and item.get('type') == 'video'), {})
    if not isinstance(streams, dict):
        streams = {}
    width = report.get('width') or streams.get('width') if isinstance(report, dict) else streams.get('width')
    height = report.get('height') or streams.get('height') if isinstance(report, dict) else streams.get('height')
    duration = report.get('duration') if isinstance(report, dict) else None
    if duration is None:
        duration = meta.get('duration')
    if duration is None and isinstance(report, dict):
        duration = report.get('expected_duration_seconds') or report.get('duration_seconds')
    if duration is None and use_timeline and timeline:
        duration = timeline.get('expected_duration')
    try:
        duration = round(float(duration), 2) if duration is not None else None
    except (TypeError, ValueError):
        duration = None
    try:
        width, height = int(width), int(height)
    except (TypeError, ValueError):
        resolution = report.get('resolution') if isinstance(report, dict) else None
        match = re.fullmatch(r'\s*(\d{2,5})\s*[x×]\s*(\d{2,5})\s*', str(resolution or ''), re.IGNORECASE)
        width, height = (int(match.group(1)), int(match.group(2))) if match else (None, None)
    return {'duration': duration, 'width': width, 'height': height}


def _folder_title(name: str) -> str:
    clean = re.sub(r'[-_]\d{8}$', '', name)
    title = re.sub(r'[-_]+', ' ', clean).strip().title()
    return re.sub(r'\b(\d+)S\b', r'\1s', title)


def _project_record(folder: Path, root: Path) -> dict:
    rel = folder.relative_to(root).as_posix()
    read_local_json = lambda name: read_json(folder / name) if is_safe_file(folder / name, root) else None
    plan = read_local_json('plan.json')
    log = read_local_json('production-log.json')
    review = read_local_json('review.json')
    timeline = read_local_json('timeline.json')
    tracks = read_local_json('audio-tracks.json')
    storyboard = read_local_json('storyboard.json')
    ledger = read_local_json('asset-ledger.json')
    plan = plan if isinstance(plan, dict) else None
    review = review if isinstance(review, dict) else None
    timeline = timeline if isinstance(timeline, dict) else None
    tracks = tracks if isinstance(tracks, dict) else None
    storyboard = storyboard if isinstance(storyboard, dict) else None
    ledger = ledger if isinstance(ledger, dict) else None
    entries = log if isinstance(log, list) else []
    log_status, stages = _log_info(entries)
    video_paths = _deliverable_videos(folder, root)
    videos = []
    for video_path in video_paths:
        report = _video_review(folder, video_paths, video_path)
        details = _video_metadata(report, timeline, len(video_paths) == 1)
        videos.append({
            'name': video_path.name,
            'title': re.sub(r'[-_]+', ' ', video_path.stem).strip().title(),
            'duration': details['duration'],
            'width': details['width'],
            'height': details['height'],
            'size': video_path.stat().st_size,
        })
    has_video = bool(videos)
    primary_video = next((video for video in videos if video['name'].lower() == 'final.mp4'), videos[0] if videos else None)
    primary_report = _video_review(folder, video_paths, Path(primary_video['name'])) if primary_video else (review or {})
    reports = sorted(path.name for path in folder.iterdir()
                     if path.suffix.lower() == '.json' and 'review' in path.stem.lower()
                     and is_safe_file(path, root))

    if log_status == 'failed':
        status = 'failed'
    elif has_video:
        status = 'complete'
    elif plan or entries:
        status = 'in_progress'
    else:
        status = 'unknown'

    fmt = timeline.get('format', {}) if timeline else {}
    if not isinstance(fmt, dict):
        fmt = {}
    width = (primary_video or {}).get('width') or fmt.get('width')
    height = (primary_video or {}).get('height') or fmt.get('height')
    duration = (primary_video or {}).get('duration')
    if duration is None and tracks:
        duration = tracks.get('duration')
    try:
        duration = round(float(duration), 2) if duration is not None else None
    except (TypeError, ValueError):
        duration = None
    try:
        width, height = int(width), int(height)
    except (TypeError, ValueError):
        width = height = None

    beats = plan.get('beats', []) if plan else []
    visuals = [visual for beat in beats if isinstance(beat, dict)
               for visual in (beat.get('visuals', []) if isinstance(beat.get('visuals', []), list) else [])
               if isinstance(visual, dict)]
    stock_count = sum(visual.get('kind') == 'stock' for visual in visuals)
    flow_count = sum(visual.get('kind') == 'google_flow' for visual in visuals)
    graphic_count = sum(visual.get('kind') in {'process', 'chart', 'cycle', 'comparison'} for visual in visuals)
    storyboard_files = [path.name for path in folder.iterdir()
                        if path.stem.lower().startswith('storyboard') and path.suffix.lower() in {'.md', '.html', '.json'}
                        and is_safe_file(path, root)]
    artifacts = {name: is_safe_file(folder / name, root) for name in ARTIFACTS}
    artifacts.update({name: True for name in storyboard_files})

    if primary_report and isinstance(primary_report.get('creative_review'), str) and 'pending' in primary_report['creative_review'].lower():
        creative_review = 'pending'
    elif primary_report and (primary_report.get('creative_review_status') in {'complete', 'approved'}
                             or primary_report.get('review_status') in {'pass', 'passed', 'approved'}):
        creative_review = 'complete'
    elif primary_report:
        creative_review = 'pending'
    else:
        creative_review = None
    milestones = [
        _milestone('Plan', plan is not None or artifacts['shots.json'] or artifacts['timeline.json']),
        _milestone('Storyboard', bool(storyboard_files)),
        _milestone('Narration & audio', artifacts.get('audio-tracks.json', False) or bool(stages.get('audio_mix') == 'complete') or bool(primary_report.get('voice'))),
        _milestone('Captions', artifacts['captions.srt'] or artifacts['captions.ass'] or artifacts['captions.json'] or bool(primary_report.get('caption_style') or primary_report.get('caption_count'))),
        _milestone('Final render', has_video),
        _milestone('Creative review', True if creative_review == 'complete' else None if creative_review == 'pending' else False),
    ]

    modified = max((p.lstat().st_mtime for p in folder.iterdir()), default=folder.stat().st_mtime)
    try:
        modified = datetime.fromtimestamp(modified, timezone.utc).isoformat()
    except (OSError, OverflowError, ValueError):
        modified = None
    report_title = (primary_video or {}).get('title') if folder.name.lower() in {'outputs', 'output'} else None
    title = str((plan or {}).get('title') or (storyboard or {}).get('title') or report_title or _folder_title(folder.name))[:180]
    if status == 'failed' and log:
        latest_error = next((entry.get('details', {}).get('error') for entry in reversed(entries)
                             if isinstance(entry, dict) and entry.get('stage') == 'production_failed'
                             and isinstance(entry.get('details'), dict)), None)
    else:
        latest_error = None

    return {
        'id': hashlib.sha256(rel.encode('utf-8')).hexdigest()[:16],
        'title': title,
        'path': rel or '.',
        'brief': str((plan or {}).get('brief') or (storyboard or {}).get('brief') or '')[:1000],
        'status': status,
        'updated_at': modified,
        'duration': duration,
        'width': width,
        'height': height,
        'fps': (fmt.get('fps') if isinstance(fmt.get('fps'), (int, float)) else None),
        'shot_count': len(visuals) or (review.get('shots') if review else None),
        'stock_count': stock_count if visuals else None,
        'flow_count': flow_count if visuals else None,
        'graphic_count': graphic_count if visuals else None,
    'voice': _voice_info(folder / 'CREDITS.md') if is_safe_file(folder / 'CREDITS.md', root) else {'provider': None, 'voice': None},
        'milestones': milestones,
        'creative_review': creative_review or ((primary_report or {}).get('status')),
        'latest_error': str(latest_error)[:500] if latest_error else None,
        'sources': _source_info(storyboard, ledger),
        'artifacts': {name: exists for name, exists in artifacts.items()},
        'has_video': has_video,
        'videos': videos,
        'video_count': len(videos),
        'primary_video': primary_video['name'] if primary_video else None,
        'reports': reports,
        'storyboards': storyboard_files,
    }


def scan_library(root: Path) -> list[dict]:
    """Discover generated output folders, preferring nested output folders over wrappers."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f'Library root is not a directory: {root}')
    candidates = []
    for current, dirs, files in os.walk(root, followlinks=False):
        here = Path(current)
        dirs[:] = sorted(name for name in dirs
                         if name not in SKIP_DIRS and not name.startswith('.') and not name.lower().endswith('-working'))
        deliverable_mp4s = any(Path(name).suffix.lower() == '.mp4'
                               and not name.lower().startswith('visuals')
                               and not re.search(r'(^|[-_])pilot([-_]|$)', Path(name).stem.lower())
                               and Path(name).stem.lower() != 'original-vs-revised'
                               for name in files)
        if any(marker in files for marker in MARKERS) or deliverable_mp4s:
            candidates.append(here)
    candidate_set = set(candidates)
    leaves = [folder for folder in candidates
              if any(path.suffix.lower() == '.mp4' and is_safe_file(path, root)
                     and not path.stem.lower().startswith('visuals')
                     and not re.search(r'(^|[-_])pilot([-_]|$)', path.stem.lower())
                     and path.stem.lower() != 'original-vs-revised'
                     for path in folder.iterdir())
              or not any(child != folder and folder in child.parents for child in candidate_set)]
    projects = []
    for folder in leaves:
        try:
            projects.append(_project_record(folder, root))
        except (OSError, ValueError):
            # A concurrently moved/deleted project is omitted; the next refresh will rescan.
            continue
    return sorted(projects, key=lambda item: (item['updated_at'] or '', item['title'].casefold()), reverse=True)


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, root: Path):
        self.library_root = root.resolve(strict=True)
        self.projects_lock = threading.Lock()
        self.projects = scan_library(self.library_root)
        super().__init__(address, DashboardHandler)


class DashboardHandler(BaseHTTPRequestHandler):
    server: DashboardServer

    def log_message(self, fmt, *args):
        # Keep local project titles/paths out of the terminal log.
        print(f'video-dashboard: {self.address_string()} {fmt % args}')

    def _send(self, status: int, body: bytes, content_type: str, extra: dict | None = None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; media-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/projects':
            with self.server.projects_lock:
                self.server.projects = scan_library(self.server.library_root)
                data = json.dumps({'projects': self.server.projects,
                                   'scanned_at': datetime.now(timezone.utc).isoformat()}, ensure_ascii=False).encode('utf-8')
            self._send(200, data, 'application/json; charset=utf-8')
            return
        if parsed.path.startswith('/media/'):
            self._serve_artifact(parsed.path)
            return
        rel = 'index.html' if parsed.path in {'/', '/index.html'} else parsed.path.lstrip('/')
        if rel not in {'index.html', 'dashboard.css', 'dashboard.js'}:
            self._send(404, b'Not found', 'text/plain; charset=utf-8')
            return
        target = (DASHBOARD_DIR / rel).resolve()
        if DASHBOARD_DIR.resolve() not in target.parents:
            self._send(404, b'Not found', 'text/plain; charset=utf-8')
            return
        try:
            content = target.read_bytes()
        except OSError:
            self._send(404, b'Dashboard asset not found', 'text/plain; charset=utf-8')
            return
        self._send(200, content, mimetypes.guess_type(target.name)[0] or 'application/octet-stream')

    def _serve_artifact(self, path: str):
        parts = unquote(path).split('/')
        if len(parts) != 4 or parts[1] != 'media' or not re.fullmatch(r'[a-f0-9]{16}', parts[2]):
            self._send(404, b'Not found', 'text/plain; charset=utf-8')
            return
        name = parts[3]
        project = next((p for p in self.server.projects if p['id'] == parts[2]), None)
        if not project:
            self._send(404, b'Project not found', 'text/plain; charset=utf-8')
            return
        if name not in ARTIFACTS and name not in {video['name'] for video in project.get('videos', [])} and name not in project.get('reports', []) and name not in project.get('storyboards', []):
            self._send(404, b'Not found', 'text/plain; charset=utf-8')
            return
        target = (self.server.library_root / project['path'] / name).resolve()
        try:
            target.relative_to(self.server.library_root)
            if not target.is_file() or target.stat().st_size == 0:
                raise FileNotFoundError
            size = target.stat().st_size
        except (OSError, ValueError):
            self._send(404, b'Artifact not found', 'text/plain; charset=utf-8')
            return
        content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        start, end, status = 0, size - 1, 200
        byte_range = self.headers.get('Range')
        if byte_range:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', byte_range.strip())
            if not match or not (match.group(1) or match.group(2)):
                self._send(416, b'Invalid byte range', 'text/plain; charset=utf-8', {'Content-Range': f'bytes */{size}'})
                return
            if match.group(1):
                start = int(match.group(1))
                end = min(int(match.group(2)) if match.group(2) else end, end)
            else:
                suffix = int(match.group(2))
                start = max(0, size - suffix)
            if start >= size or end < start:
                self._send(416, b'Invalid byte range', 'text/plain; charset=utf-8', {'Content-Range': f'bytes */{size}'})
                return
            status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(length))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Disposition', 'inline')
        if status == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with target.open('rb') as media:
                media.seek(start)
                remaining = length
                while remaining:
                    chunk = media.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (OSError, BrokenPipeError, ConnectionResetError):
            return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Folder containing generated output folders')
    parser.add_argument('--host', default='127.0.0.1', help='Bind address (localhost only by default)')
    parser.add_argument('--port', type=int, default=8765, help='Local dashboard port')
    parser.add_argument('--open', action='store_true', help='Open the dashboard in your default browser')
    args = parser.parse_args()
    if args.host != '127.0.0.1':
        parser.error('For privacy, --host must remain 127.0.0.1')
    try:
        root = args.root.expanduser().resolve(strict=True)
        server = DashboardServer((args.host, args.port), root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Video dashboard: {url}')
    print(f'Library: {root} (read-only; metadata stays on this computer)')
    print(f'Projects found: {len(server.projects)}')
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping dashboard.')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
