#!/usr/bin/env python3
"""Annotated matrix with an explicit scale; missing values are shown as missing."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[2]


def load_data(path):
    data = json.loads(Path(path).read_text())
    for key in ('rows', 'columns'):
        labels = data.get(key)
        if (not isinstance(labels, list) or not labels or
                any(not isinstance(v, str) or not v for v in labels) or len(set(labels)) != len(labels)):
            raise ValueError(f'{key} must contain unique nonempty labels')
    values = data.get('values')
    if not isinstance(values, list) or len(values) != len(data['rows']):
        raise ValueError('values must match rows')
    for row in values:
        if not isinstance(row, list) or len(row) != len(data['columns']):
            raise ValueError('Every value row must match columns')
        if any(v is not None and (type(v) not in (int, float) or not math.isfinite(v)) for v in row):
            raise ValueError('Values must be finite numbers or explicit null')
    if not any(v is not None for row in values for v in row):
        raise ValueError('At least one value is required')
    return data


def render(data, layout):
    plt.style.use(ROOT / 'styles/paper.mplstyle')
    values = np.array([[np.nan if v is None else v for v in row] for row in data['values']])
    lo, hi = layout['vmin'], layout['vmax']
    if not lo < hi or np.nanmin(values) < lo or np.nanmax(values) > hi:
        raise ValueError('The declared scale must include all values')
    center = layout.get('center')
    if center is not None:
        if not lo < center < hi:
            raise ValueError('center must be inside the scale')
        cmap = LinearSegmentedColormap.from_list('signed', ['#BA5C2A', '#FFFFFF', '#216E91'])
        norm = TwoSlopeNorm(vmin=lo, vcenter=center, vmax=hi)
    else:
        cmap = LinearSegmentedColormap.from_list('counts', ['#FFFFFF', '#A6CFD3', '#165D79'])
        norm = Normalize(vmin=lo, vmax=hi)
    cmap.set_bad('#DADADA')
    fig, ax = plt.subplots(figsize=layout.get('figsize', [7.16, 4]))
    fig.subplots_adjust(**layout.get('margins', dict(left=.27, right=.95, bottom=.16, top=.96)))
    im = ax.imshow(np.ma.masked_invalid(values), cmap=cmap, norm=norm, aspect=layout.get('aspect', 'auto'))
    ax.set_xticks(range(len(data['columns'])), data['columns'])
    ax.set_yticks(range(len(data['rows'])), data['rows'])
    ax.tick_params(axis='both', length=0)
    ax.tick_params(axis='x', labelrotation=layout.get('rotation', 0))
    ax.set_xticks(np.arange(-.5, len(data['columns']), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(data['rows']), 1), minor=True)
    ax.grid(which='minor', color='#FFFFFF', linewidth=.7)
    ax.tick_params(which='minor', bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fmt = layout.get('format', '.0f')
    for i, row in enumerate(data['values']):
        for j, value in enumerate(row):
            if value is None:
                text, color = 'NA', '#333333'
            else:
                text = format(value, fmt)
                rgba = cmap(norm(value))
                luminance = .2126 * rgba[0] + .7152 * rgba[1] + .0722 * rgba[2]
                color = '#FFFFFF' if luminance < .48 else '#222222'
            ax.text(j, i, text, ha='center', va='center', color=color,
                    fontsize=layout.get('annotation_size', 8))
    colorbar = fig.colorbar(im, ax=ax, orientation='horizontal', fraction=.045, pad=layout.get('colorbar_pad', .09), aspect=35)
    colorbar.set_label(layout.get('colorbar_label', 'Value'))
    if 'colorbar_ticks' in layout:
        colorbar.set_ticks(layout['colorbar_ticks'])
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path(__file__).with_name('data.json'))
    parser.add_argument('--layout', type=Path, default=Path(__file__).with_name('layout.json'))
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/matrix')
    args = parser.parse_args()
    data, layout = load_data(args.data), json.loads(args.layout.read_text())
    fig = render(data, layout)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    name = layout.get('output_name', 'annotated-matrix')
    if Path(name).name != name:
        raise ValueError('output_name must be a filename stem')
    for suffix in ('pdf', 'png'):
        kwargs = {'metadata': {'Author': '', 'Subject': 'Descriptive matrix; scale explicit'}} if suffix == 'pdf' else {}
        fig.savefig(args.output_dir / f'{name}.{suffix}', dpi=300, **kwargs)
    (args.output_dir / f'{name}.render.json').write_text(json.dumps({
        'data_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
        'layout_sha256': hashlib.sha256(args.layout.read_bytes()).hexdigest(),
        'matplotlib': matplotlib.__version__, 'layout': layout}, indent=2) + '\n')
    plt.close(fig)
    print(args.output_dir / f'{name}.pdf')


if __name__ == '__main__':
    main()
