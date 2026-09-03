#!/usr/bin/env python3
"""Turn Lighthouse CI reports into compact, machine-readable GrowthProof evidence."""
from __future__ import annotations

import glob
import json
import os
import statistics
from pathlib import Path

REPORT_DIR = Path('.lighthouseci/reports')


def median(values):
    return statistics.median(values) if values else None


def fmt(value, digits=0):
    if value is None:
        return 'n/a'
    return f'{value:.{digits}f}'


def main() -> int:
    reports = []
    for name in glob.glob(str(REPORT_DIR / '*.json')):
        try:
            payload = json.loads(Path(name).read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get('categories') and payload.get('audits'):
            reports.append(payload)

    if not reports:
        raise SystemExit('No Lighthouse LHR JSON reports found.')

    def category(key):
        values = [r['categories'][key]['score'] * 100 for r in reports if key in r.get('categories', {})]
        return median(values)

    def audit(key):
        values = [r['audits'][key]['numericValue'] for r in reports
                  if key in r.get('audits', {}) and r['audits'][key].get('numericValue') is not None]
        return median(values)

    summary = {
        'runs': len(reports),
        'performance_score': category('performance'),
        'accessibility_score': category('accessibility'),
        'best_practices_score': category('best-practices'),
        'seo_score': category('seo'),
        'largest_contentful_paint_ms': audit('largest-contentful-paint'),
        'cumulative_layout_shift': audit('cumulative-layout-shift'),
        'total_blocking_time_ms': audit('total-blocking-time'),
        'speed_index_ms': audit('speed-index'),
        'total_byte_weight_bytes': audit('total-byte-weight'),
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / 'growthproof-summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8'
    )

    rows = [
        ('Performance', fmt(summary['performance_score'])),
        ('Accessibility', fmt(summary['accessibility_score'])),
        ('Best practices', fmt(summary['best_practices_score'])),
        ('SEO', fmt(summary['seo_score'])),
        ('LCP', fmt(summary['largest_contentful_paint_ms']) + ' ms'),
        ('CLS', fmt(summary['cumulative_layout_shift'], 3)),
        ('TBT', fmt(summary['total_blocking_time_ms']) + ' ms'),
        ('Speed Index', fmt(summary['speed_index_ms']) + ' ms'),
        ('Transfer weight', fmt((summary['total_byte_weight_bytes'] or 0) / 1024) + ' KiB'),
    ]

    print(f"GrowthProof Lighthouse median from {len(reports)} run(s)")
    for label, value in rows:
        print(f'{label}: {value}')

    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8') as handle:
            handle.write(f'### GrowthProof Lighthouse median ({len(reports)} runs)\n\n')
            handle.write('| Metric | Median |\n|---|---:|\n')
            for label, value in rows:
                handle.write(f'| {label} | {value} |\n')
            handle.write('\n')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
