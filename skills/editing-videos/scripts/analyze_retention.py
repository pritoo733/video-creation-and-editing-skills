"""Describe normalized audience-retention samples and align declines to planned beats; no APIs."""
import argparse
import csv
import json
import math
from pathlib import Path


def analyze(rows, beats=()):
    points = []
    for row in rows:
        t, value = float(row['seconds']), float(row['retention_percent'])
        if not math.isfinite(t) or not math.isfinite(value) or min(t, value) < 0:
            raise ValueError('Retention values and seconds must be finite and nonnegative')
        if points and t <= points[-1][0]: raise ValueError('Sample times must be strictly increasing')
        points.append((t, value))
    if len(points) < 2: raise ValueError('Provide at least two retention samples')
    for beat in beats:
        start, end = beat['start'], beat['end']
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (start, end)) or end <= start:
            raise ValueError('Beat intervals must be finite with end after start')
    declines = []
    opening_at_30 = None
    for (start, before), (end, after) in zip(points, points[1:]):
        loss = before - after
        if loss > 0:
            matching = [b['id'] for b in beats if b['start'] < end and b['end'] > start]
            declines.append(dict(start=start, end=end, drop_percentage_points=round(loss, 4),
                                 drop_pp_per_second=round(loss / (end - start), 4), beat_ids=matching))
        if start <= 30 <= end:
            opening_at_30 = before + (after - before) * (30 - start) / (end - start)
    declines.sort(key=lambda row: row['drop_percentage_points'], reverse=True)
    return dict(observed_start=points[0][0], observed_end=points[-1][0], samples=len(points),
                change_first_observed_to_last_pp=round(points[-1][1] - points[0][1], 4),
                first_30s_drop_pp=round(points[0][1] - opening_at_30, 4) if points[0][0] == 0 and opening_at_30 is not None else None,
                first_30s_method='Linear interpolation between samples; only available when samples cover zero to 30 seconds',
                largest_declines=declines[:5],
                interpretation='Observed changes, not proof of why viewers left. Replays can exceed 100%; compare matched audiences and inspect footage/transcript before proposing a fix.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path, help='UTF-8 CSV with explicit seconds,retention_percent headers')
    parser.add_argument('--plan', type=Path, help='Optional script package containing a beats array')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        with args.csv.open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        beats = json.loads(args.plan.read_text(encoding='utf-8'))['beats'] if args.plan else []
        result = analyze(rows, beats)
        text = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text + '\n', encoding='utf-8')
        else: print(text)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f'Invalid retention data: {exc}\n')


if __name__ == '__main__':
    main()
