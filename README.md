# Paper Plot Studio

A small, readable collection of Python examples for paper figures. Keep research data outside the repository, adapt a plotting script, and export a vector PDF for LaTeX/Overleaf plus a PNG preview.

**Current scope:** one pass-rate line-chart example using Matplotlib. This is a starter collection, not a general chart editor or statistics package. The included data are explicitly synthetic and do not report experimental results.

Learning with this project? Start with the [中文入门指南：读懂命令、修改图表并导入 Overleaf](docs/getting-started.zh-CN.md). It explains each command and suggests small exercises using the synthetic example.

## Quick start

Requires Python 3.9+ and a POSIX shell (macOS/Linux; on Windows, use WSL). From the downloaded project directory:

```sh
./setup.sh
./draw.sh line
```

Setup creates a local `.venv`. Matplotlib 3.9.4 is the tested baseline, not a claim about the latest release. Fonts use Times New Roman when available and fall back to DejaVu Serif; system LaTeX is not required.

Generated files:

- `outputs/line/line-comparison.pdf` — vector figure for the paper.
- `outputs/line/line-comparison.png` — preview for local inspection.

## Use your own data

Copy `examples/line/data.json` to a directory **outside this repository**, then replace the synthetic values:

```sh
./draw.sh line --data ../my-paper-data/results.json --output-dir ../my-paper-data/figures
```

The JSON format is intentionally small:

```json
{
  "conditions": ["Setting A", "Setting B", "Setting C"],
  "series": [
    {"label": "Method A", "n": 100, "passes": [45, 60, 80]}
  ]
}
```

`n` is the fixed denominator for that series across all conditions. Each pass count must be an integer between zero and `n`. A series may optionally set `color` and `marker`. The script calculates `passes / n`; it does not pool data, select samples, impute missing values, or run statistical tests. If denominators differ between conditions, adapt the data model and script before using them.

The number of conditions and series is variable. Connecting conditions with lines should make sense for your comparison. Long labels, dense curves, and similar values can still overlap: inspect and adjust the figure at its final paper width.

## Keep rendering code public and paper-specific inputs private

The same in-project renderer supports both the synthetic example and your paper. You do not need a separate Python script in your private data directory. Save paper-specific layout settings in an external JSON file:

```sh
./draw.sh line \
  --data ../my-paper-data/results.json \
  --layout ../my-paper-data/layout.json \
  --output-dir ../my-paper-data/figures
```

Try the public layout example with `./draw.sh line --layout examples/line/layout.json`.

Layout keys include `figsize` (inches), `margins` (figure fractions), `ylabel`, `y_min`, `legend` (Matplotlib legend keyword arguments), and `output_name` (filename stem). `--y-min` and `--output-name` override the corresponding layout values. Without a layout file, the original example defaults apply.

Optional `annotations` is a list with one row per series and one object per condition. Each object specifies `xytext: [x, y]` and optionally `textcoords: "offset points"` (default) or `"data"`. For example, `{"xytext": [0, 7]}` places a label seven points above its data point; `{"xytext": [2, 0.9], "textcoords": "data"}` puts it at condition index 2 and rate 0.9. The row and column order follows the data JSON. `annotation_va` controls vertical alignment, and `annotation_box` accepts Matplotlib text bounding-box settings. This is explicit label positioning, not automatic overlap detection.

To change the axis lower bound:

```sh
./draw.sh line --y-min 0.2
```

The lower bound is a fraction (`0.2` means 20%) and must not hide any data point. A nonzero baseline changes how differences look; choose it deliberately and keep tick labels visible.

## What to edit

| Goal | File or code |
| --- | --- |
| Learn with invented data | `examples/line/data.json` |
| Plot real results | An external JSON file passed with `--data` |
| Change lines, legend, axes, or annotations | `examples/line/plot.py` |
| Keep a paper's layout separate from reusable code | An external JSON file passed with `--layout` |
| Change shared fonts | `styles/paper.mplstyle` |
| Change the figure size | `figsize` in the plotting script |

The 3.48-inch figure width and 8-point base font are example settings, not universal venue requirements. Check the instructions for your own paper template. Matplotlib supplies the plotting engine; this project adds examples and workflow conventions.

## Use with Overleaf

1. Run the script and inspect the PNG.
2. Upload the generated PDF to your Overleaf project, for example under `Figures/`.
3. Include it in the manuscript:

```latex
% In the preamble:
\usepackage{graphicx}

% In the document:
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{Figures/line-comparison.pdf}
  \caption{Describe the actual experiment and data selection.}
  \label{fig:comparison}
\end{figure}
```

On later updates, upload a same-named PDF and recompile. Captions and manuscript text are maintained in LaTeX; they are not updated automatically by the plotting script.

## Project layout

```text
examples/line/    Synthetic input and a readable plotting script
docs/            Step-by-step learning guides
styles/          Shared Matplotlib style
tests/           CLI and data-validation checks
outputs/         Generated figures (Git-ignored)
setup.sh         Local environment setup
draw.sh          Example runner
LICENSE          MIT license for this project's original files
```

Add new examples under `examples/NAME/plot.py`, with clearly labeled synthetic data and documentation. Then use `./draw.sh NAME`. Keep examples runnable without access to private files. Changes to one example should not require other papers' datasets.

## Development and privacy

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Research inputs, unpublished results, generated research figures, manuscript sources, credentials, and private project links should remain outside the public repository. `.gitignore` excludes the environment, generated outputs, and common private-data paths; it is a convenience, not a detector for sensitive files or a way to remove committed history. Inspect the files and Git history before publishing.

The source code, public documentation, and synthetic example data are licensed under [MIT](LICENSE). External research datasets are not included or licensed by this project. Matplotlib and other installed dependencies retain their own licenses; their source and fonts are not vendored here.

## 中文入门

完整步骤见[中文入门指南](docs/getting-started.zh-CN.md)，涵盖命令解释、输出位置、数据与布局分工，以及 Overleaf 操作。

先运行 `./setup.sh`，再运行 `./draw.sh line`。所有绘图实现都在本项目中。示例中的数字均为模拟数据；真实论文数据和专用布局放在项目外，通过 `--data` 和 `--layout` 指定，无需在私有目录里维护另一套绘图代码。PDF 用于上传 Overleaf，PNG 用于检查布局。先看懂一个示例，再按自己的论文需求增加图型。
