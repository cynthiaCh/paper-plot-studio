#!/usr/bin/env python3
"""Paired binary transitions; denominators are matched observations, not marginals."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]


def load_data(path):
    data = json.loads(Path(path).read_text())
    rows = data.get('series', [])
    if not rows:
        raise ValueError('series must be nonempty')
    ids = []
    for row in rows:
        ids.append(row.get('id'))
        if not isinstance(row.get('label'), str) or not row['label'].strip():
            raise ValueError('Each series needs a label')
        n, fp, pf = (row.get(k) for k in ('n', 'fp', 'pf'))
        if type(n) is not int or n <= 0:
            raise ValueError('n must be a positive integer')
        if any(type(v) is not int or v < 0 for v in (fp, pf)) or fp + pf > n:
            raise ValueError('fp and pf must be disjoint nonnegative counts with sum <= n')
    if any(not isinstance(v, str) or not v for v in ids) or len(set(ids)) != len(ids):
        raise ValueError('Stable unique series ids are required')
    return data


def render(data, layout):
    rows = data['series']
    plt.style.use(ROOT / 'styles/paper.mplstyle')
    fig, ax = plt.subplots(figsize=layout.get('figsize', [7.16, max(2.1, .24 * len(rows) + 1)]))
    fig.subplots_adjust(**layout.get('margins', dict(left=.29, right=.81, bottom=.12, top=.91)))
    y = list(range(len(rows)))
    pos = [100 * r['fp'] / r['n'] for r in rows]
    neg = [-100 * r['pf'] / r['n'] for r in rows]
    colors = layout.get('colors', {'fp': '#247A8B', 'pf': '#C46A30'})
    ax.barh(y, pos, height=.63, color=colors['fp'], label='Fail to pass (FP)')
    ax.barh(y, neg, height=.63, color=colors['pf'], label='Pass to fail (PF)')
    ax.axvline(0, color='#444444', lw=.7)
    ax.set_yticks(y, [r['label'] for r in rows])
    ax.invert_yaxis()
    ax.set_ylim(len(rows) - .5, -.5)
    bounds = layout.get('xlim', [-max(5, max(-v for v in neg) * 1.25), max(pos) * 1.12])
    if bounds[0] > min(neg) or bounds[1] < max(pos):
        raise ValueError('xlim must not hide transitions')
    ax.set_xlim(bounds)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{abs(x):g}'))
    ax.set_xlabel(layout.get('xlabel', 'Share of matched pairs (%)'))
    ax.xaxis.grid(True, color='#E3E3E3', lw=.45)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', length=0)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    for i, row in enumerate(rows):
        ax.text(1.04, i, str(row['n']), transform=ax.get_yaxis_transform(), ha='right', va='center')
        delta = 100 * (row['fp'] - row['pf']) / row['n']
        ax.text(1.24, i, f'{delta:+.2f}', transform=ax.get_yaxis_transform(), ha='right', va='center')
    for x, text in [(1.04, 'N'), (1.24, 'Gain (pp)')]:
        ax.text(x, 1.025, text, transform=ax.transAxes, ha='right', va='bottom', fontweight='bold')
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.025), ncols=2, frameon=False,
              handlelength=1.1, columnspacing=1.2, borderaxespad=0)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path(__file__).with_name('data.json'))
    parser.add_argument('--layout', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/paired')
    args = parser.parse_args()
    data = load_data(args.data)
    layout = json.loads(args.layout.read_text()) if args.layout else {}
    fig = render(data, layout)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    name = layout.get('output_name', 'paired-transitions')
    if Path(name).name != name:
        raise ValueError('output_name must be a filename stem')
    for suffix in ('pdf', 'png'):
        kwargs = {'metadata': {'Author': '', 'Subject': 'Descriptive matched binary transitions'}} if suffix == 'pdf' else {}
        fig.savefig(args.output_dir / f'{name}.{suffix}', dpi=300, **kwargs)
    provenance = {'data_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
                  'layout_sha256': hashlib.sha256(args.layout.read_bytes()).hexdigest() if args.layout else None,
                  'matplotlib': matplotlib.__version__, 'series': data['series'], 'layout': layout}
    (args.output_dir / f'{name}.render.json').write_text(json.dumps(provenance, indent=2) + '\n')
    plt.close(fig)
    print(args.output_dir / f'{name}.pdf')


if __name__ == '__main__':
    main()
