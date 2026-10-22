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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA,
                        help='JSON input; defaults to the synthetic example')
    parser.add_argument('--output-dir', type=Path,
                        default=PROJECT_ROOT / 'outputs/line')
    parser.add_argument('--y-min', type=float, default=0,
                        help='Y-axis lower bound as a fraction, e.g. 0.2 = 20%%')
    args = parser.parse_args()
    try:
        record = load_data(args.data)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rates = [[v / row['n'] for v in row['passes']] for row in record['series']]
    if (not math.isfinite(args.y_min) or args.y_min < 0
            or args.y_min > min(min(values) for values in rates)):
        parser.error('--y-min must be finite, nonnegative, and not hide any data point')

    plt.style.use(PROJECT_ROOT / 'styles/paper.mplstyle')
    fig, ax = plt.subplots(figsize=(3.48, 2.80))
    fig.subplots_adjust(left=.17, right=.94, bottom=.17, top=.94)
    positions = list(range(len(record['conditions'])))
    for index, (row, values) in enumerate(zip(record['series'], rates)):
        color = row.get('color', f'C{index % 10}')
        ax.plot(positions, values, color=color, marker=row.get('marker', 'o'),
                lw=1.15, ms=4, label=row['label'])
        for position, count, rate in zip(positions, row['passes'], values):
            ax.annotate(f"{count}/{row['n']}", (position, rate), xytext=(0, 7),
                        textcoords='offset points', ha='center', va='bottom',
                        fontsize=6.8, color=color)
    ax.set_xticks(positions, record['conditions'])
    ax.set_xlim(-.2, len(positions) - .8)
    ax.set_ylim(args.y_min, 1.12)
    ax.set_yticks([v / 5 for v in range(6) if v / 5 >= args.y_min])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel('Pass rate')
    ax.grid(axis='y', color='#dddddd', lw=.5)
    ax.set_axisbelow(True)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.legend(loc='lower right', frameon=False, fontsize=7)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ['pdf', 'png']:
        output = args.output_dir / f'line-comparison.{suffix}'
        fig.savefig(output, **({'dpi': 200} if suffix == 'png' else {}))
        print(output)
    plt.close(fig)


if __name__ == '__main__':
    main()
