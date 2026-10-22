#!/usr/bin/env python3
"""Plot pass rates from JSON; export vector PDF and preview PNG."""
import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = Path(__file__).with_name('data.json')


def load_data(path):
    record = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(record, dict):
        raise ValueError('The JSON root must be an object')
    conditions = record.get('conditions')
    if (not isinstance(conditions, list) or len(conditions) < 2
            or any(not isinstance(v, str) or not v.strip() for v in conditions)):
        raise ValueError('conditions must contain at least two nonempty labels')
    series = record.get('series')
    if not isinstance(series, list) or not series:
        raise ValueError('series must be a nonempty list')
    for row in series:
        if not isinstance(row, dict):
            raise ValueError('Each series must be an object')
        label, n, counts = row.get('label'), row.get('n'), row.get('passes')
        if not isinstance(label, str) or not label.strip():
            raise ValueError('Each series needs a nonempty label')
        if type(n) is not int or n <= 0:
            raise ValueError('Each series needs a positive integer n')
        if not isinstance(counts, list) or len(counts) != len(conditions):
            raise ValueError('Each passes list must match the number of conditions')
        if any(type(v) is not int or not 0 <= v <= n for v in counts):
            raise ValueError('Pass counts must be integers between zero and n')
    return record


def load_layout(path, record):
    layout = json.loads(path.read_text(encoding='utf-8')) if path else {}
    if not isinstance(layout, dict):
        raise ValueError('The layout JSON root must be an object')
    annotations = layout.get('annotations')
    if annotations is not None:
        if not isinstance(annotations, list) or len(annotations) != len(record['series']):
            raise ValueError('annotations must have one row per data series')
        for row in annotations:
            if not isinstance(row, list) or len(row) != len(record['conditions']):
                raise ValueError('Each annotation row must match the number of conditions')
            for item in row:
                if not isinstance(item, dict):
                    raise ValueError('Each annotation must be an object')
                offset = item.get('xytext')
                if (not isinstance(offset, list) or len(offset) != 2
                        or any(type(v) not in (int, float) or not math.isfinite(v) for v in offset)):
                    raise ValueError('Each annotation needs two finite xytext coordinates')
                if item.get('textcoords', 'offset points') not in ('offset points', 'data'):
                    raise ValueError('Annotation textcoords must be offset points or data')
    return layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA,
                        help='JSON input; defaults to the synthetic example')
    parser.add_argument('--layout', type=Path,
                        help='Optional layout JSON (legend, margins, annotation positions)')
    parser.add_argument('--output-name', help='Output filename stem; overrides layout output_name')
    parser.add_argument('--output-dir', type=Path,
                        default=PROJECT_ROOT / 'outputs/line')
    parser.add_argument('--y-min', type=float,
                        help='Y-axis lower bound as a fraction, e.g. 0.2 = 20%%')
    args = parser.parse_args()
    try:
        record = load_data(args.data)
        layout = load_layout(args.layout, record)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rates = [[v / row['n'] for v in row['passes']] for row in record['series']]
    y_min = args.y_min if args.y_min is not None else layout.get('y_min', 0)
    if (type(y_min) not in (int, float) or not math.isfinite(y_min) or y_min < 0
            or y_min > min(min(values) for values in rates)):
        parser.error('--y-min must be finite, nonnegative, and not hide any data point')
    output_name = args.output_name or layout.get('output_name', 'line-comparison')
    if (not isinstance(output_name, str) or not output_name.strip()
            or output_name in ('.', '..') or '/' in output_name or '\\' in output_name):
        parser.error('output name must be a filename stem, not a path')

    plt.style.use(PROJECT_ROOT / 'styles/paper.mplstyle')
    fig, ax = plt.subplots(figsize=layout.get('figsize', [3.48, 2.80]))
    margins = dict(left=.17, right=.94, bottom=.17, top=.94)
    margins.update(layout.get('margins', {}))
    fig.subplots_adjust(**margins)
    positions = list(range(len(record['conditions'])))
    for index, (row, values) in enumerate(zip(record['series'], rates)):
        color = row.get('color', f'C{index % 10}')
        ax.plot(positions, values, color=color, marker=row.get('marker', 'o'),
                lw=1.15, ms=4, label=row['label'])
        for position, count, rate in zip(positions, row['passes'], values):
            annotation = (layout['annotations'][index][position]
                          if layout.get('annotations') is not None else {})
            ax.annotate(f"{count}/{row['n']}", (position, rate),
                        xytext=annotation.get('xytext', [0, 7]),
                        textcoords=annotation.get('textcoords', 'offset points'),
                        ha='center', va=layout.get('annotation_va', 'bottom'),
                        fontsize=6.8, color=color, bbox=layout.get('annotation_box'))
    ax.set_xticks(positions, record['conditions'])
    ax.set_xlim(-.2, len(positions) - .8)
    ax.set_ylim(y_min, 1.12)
    ax.set_yticks([v / 5 for v in range(6) if v / 5 >= y_min])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel(layout.get('ylabel', 'Pass rate'))
    ax.grid(axis='y', color='#dddddd', lw=.5)
    ax.set_axisbelow(True)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    legend = dict(loc='lower right', frameon=False, fontsize=7)
    legend.update(layout.get('legend', {}))
    ax.legend(**legend)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ['pdf', 'png']:
        output = args.output_dir / f'{output_name}.{suffix}'
        fig.savefig(output, **({'dpi': 200} if suffix == 'png' else {}))
        print(output)
    plt.close(fig)


if __name__ == '__main__':
    main()
