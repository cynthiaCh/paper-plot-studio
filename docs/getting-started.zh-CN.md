# 从一条命令开始学习论文绘图

先画出一张图，再每次修改一个参数，观察图片怎样变化。本文使用项目自带的模拟数据，不需要真实论文数据，也不需要先读完 Matplotlib 文档。

## 1. 先运行自带示例

如果终端当前位于项目的上一级目录，执行：

```bash
cd paper-plot-studio
./setup.sh
./draw.sh line
```

如果已经在项目目录，跳过 `cd`。`./setup.sh` 在第一次使用或安装依赖时运行；后续通常只需执行 `./draw.sh line`。

| 命令 | 做什么 |
| --- | --- |
| `cd paper-plot-studio` | 进入项目目录 |
| `./setup.sh` | 创建本项目的 Python 环境 `.venv` 并安装依赖 |
| `./draw.sh line` | 使用项目内的折线图代码生成图片 |

终端会打印输出路径。默认生成：

```text
outputs/line/line-comparison.pdf
outputs/line/line-comparison.png
```

PNG 用于本地预览，PDF 用于论文。两者来自同一次绘图。

## 2. 读懂一条完整的绘图命令

下面这条命令完全可以运行，仍然使用模拟数据，只是把成品命名为 `fig5` 并存放到 `outputs/fig5/`：

```bash
./draw.sh line \
  --data examples/line/data.json \
  --layout examples/line/layout.json \
  --output-name fig5 \
  --output-dir outputs/fig5
```

| 部分 | 含义 |
| --- | --- |
| `./draw.sh` | 运行当前项目的入口，自动使用 `.venv` 中的 Python |
| `line` | 选择折线图，对应 `examples/line/plot.py` |
| `--data examples/line/data.json` | 指定数据文件：条件、方法名称、样本数、通过数等 |
| `--layout examples/line/layout.json` | 指定布局文件：图尺寸、图例、纵轴起点、标注位置等 |
| `--output-name fig5` | 指定文件名，不需要写 `.pdf` 或 `.png` 后缀 |
| `--output-dir outputs/fig5` | 指定输出文件夹，相对于运行命令时终端所在的目录 |

这次生成的是：

```text
outputs/fig5/fig5.pdf
outputs/fig5/fig5.png
```

`fig5` 是本例指定的文件名；论文中显示的“Fig. 5”编号由 LaTeX 按图的顺序生成，改图片文件名不会改变论文编号。

## 3. 理解路径和换行符

| 写法 | 含义 |
| --- | --- |
| `./` | 当前目录 |
| `../` | 上一级目录 |
| `../my-paper-data/` | 项目旁边的一个数据文件夹 |
| 每行末尾的 `\` | 命令尚未结束，下一行接着写 |

反斜杠后不要再加空格。也可以把完整命令写成一行：

```bash
./draw.sh line --data examples/line/data.json --layout examples/line/layout.json --output-name fig5 --output-dir outputs/fig5
```

路径有空格时，用引号包住整个路径，例如 `--data "../my paper data/results.json"`。

本文的终端命令使用 Bash/shell 语法，代码块标记为 `bash`；它们不是 Swift 代码。

## 4. 真正画自己的论文图

绘图实现始终使用本项目的代码。把真实数据和该论文的布局配置存放在项目外即可：

```text
同一个父目录/
├── paper-plot-studio/           # 可以公开的代码、说明和模拟示例
└── my-paper-data/              # 自己维护的私有论文输入
    └── fig5/
        ├── data.json
        └── layout.json
```

如果还没有自己的输入文件，可以先复制模拟示例，再逐步修改：

```bash
mkdir -p ../my-paper-data/fig5
cp examples/line/data.json ../my-paper-data/fig5/data.json
cp examples/line/layout.json ../my-paper-data/fig5/layout.json
```

替换并核对好数据后，从项目目录运行：

```bash
./draw.sh line \
  --data ../my-paper-data/fig5/data.json \
  --layout ../my-paper-data/fig5/layout.json \
  --output-name fig5 \
  --output-dir outputs/fig5
```

这里的 `my-paper-data` 是示例目录名，需要换成自己的真实路径。公开文档不包含任何人的真实研究数据、私人项目链接或本机绝对路径。

也可以把 `--output-dir` 改成 `../my-paper-data/figures/fig5`，将成品放到项目外。以命令打印的路径为准，不要只在当前项目中寻找。

## 5. 修改时应该打开哪个文件

| 想修改什么 | 修改哪里 |
| --- | --- |
| 条件名称 | 数据 JSON 的 `conditions` |
| 每条曲线的名称 | 数据 JSON 的 `series` → `label` |
| 样本数和通过数 | 数据 JSON 的 `n`、`passes` |
| 曲线颜色和标记 | 数据 JSON 的 `color`、`marker` |
| 图尺寸 | 布局 JSON 的 `figsize`，单位为英寸 |
| 纵轴下限 | 布局 JSON 的 `y_min`，或命令参数 `--y-min` |
| 图例位置 | 布局 JSON 的 `legend` → `loc` |
| 某个数字标签的位置 | 布局 JSON 的 `annotations` |
| 共用字体 | `styles/paper.mplstyle` |
| 绘图过程本身 | `examples/line/plot.py` |

`n` 是一条曲线在所有条件下共用的分母，`passes` 按 `conditions` 的顺序排列。比如 `n=100`、`passes=[45,60,80]`，绘制的是 45%、60%、80%。分母随条件变化的数据需要先调整数据结构与计算逻辑，不能直接套用这个示例。

布局 JSON 中的 `annotations` 按“曲线 × 条件”排列。增减曲线或条件时，也要同步调整它；不传 `--layout` 则使用代码里的默认布局。

`--y-min` 和 `--output-name` 优先于布局文件里的 `y_min`、`output_name`。最终文件路径是“输出目录 + 文件名 + 后缀”。

## 6. 用三个小练习学习

先使用模拟数据，每次只改一件事，然后重新运行完整命令。

1. 给某条曲线换一个名称，确认图例随之更新。
2. 追加 `--y-min 0.2`，观察纵轴从 20% 开始。坐标起点会影响差异的视觉大小，要按表达目的选择；程序不允许下限隐藏数据点。
3. 把布局中的 `"loc": "lower right"` 改为 `"upper left"`，观察图例移动，再判断是否遮住曲线。

生成后检查名称、数值和布局，不需要先改 Python 代码。熟悉配置后，再打开 `plot.py`，依次找到 `load_data`、`ax.plot`、`ax.annotate`、`ax.legend` 和 `fig.savefig`，将自己的修改对应到这些代码。

## 7. 上传 Overleaf

1. 打开 PNG，检查名称、数值标签、图例是否清楚，有无遮挡或裁切。
2. 在 Overleaf 中上传生成的 PDF，例如放到 `Figures/` 文件夹。
3. 在 LaTeX 中引用：

```latex
% 导言区：
\usepackage{graphicx}

% 正文：
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{Figures/fig5.pdf}
  \caption{Describe the actual experiment and data selection.}
  \label{fig:comparison}
\end{figure}
```

以后更新数据或布局，重新运行同一条命令会覆盖本地同名图片。再次上传 PDF，同名覆盖 Overleaf 文件，然后点击 Recompile。

如果论文已经引用了其他文件名，使用 `--output-name` 保持原名，或者同步修改 `\includegraphics` 的路径。图注、正文和表格需要自己同步核对，不会随 Python 出图自动更新。

## 8. 找不到输出文件时

- 先看终端是否出现错误。出现错误时，不要把磁盘上的旧图当成刚生成的新图。
- 看终端最后打印的 PDF/PNG 路径；运行命令前可用 `pwd` 确认当前目录。
- 若指定 `--output-dir outputs/fig5`，可执行 `ls -lh outputs/fig5` 查看文件及修改时间。
- macOS 下可执行 `open outputs/fig5` 打开文件夹；这一步不是绘图所必需。
- `outputs/` 已被 Git 忽略，因此正常 Git 提交不会带上成品。它仍是本地真实文件夹；手动打包整个目录时也要注意排除私有内容。

返回[项目说明](../README.md)。
