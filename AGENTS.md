# Paper Plot Studio

## Scope and environment

- This is a personal experiment figure and table workspace. Extend it only for the current task.
- Reuse the existing renderer, external data/layout configuration, and `styles/paper.mplstyle` where suitable.
- Preserve `requirements.txt` and the project's Python baseline. External skill dependency pins describe their examples; they do not authorize upgrading this project or installing packages. Check compatibility before using an example.
- Installation-time environment check found Python 3.9.6 and Matplotlib 3.9.4. Some upstream bundled CLIs require Python 3.11+; their execution is not validated in this environment. Recheck the environment when using them.
- Keep real experiment data and paper-specific configuration outside the repository, as described in README.md. Never overwrite raw inputs.

## Scientific Agent Skills

The following selected skills are installed in the user's Codex skills directory (`~/.codex/skills`). Read the relevant `SKILL.md` and only the references needed for the task:

| Task | Skill |
| --- | --- |
| Paper figure design, uncertainty displays, and export inspection | `scientific-visualization` |
| Matplotlib rendering and precise layout | `matplotlib` |
| Statistical distribution plots and heatmaps | `seaborn` |
| Inspect local experiment files and missing values | `exploratory-data-analysis` |
| A requested statistical comparison or uncertainty analysis | `statistical-analysis` |

These are a selected subset of https://github.com/K-Dense-AI/scientific-agent-skills, not the full collection. Preserve their bundled references, scripts, and licensing information. Installing skills does not install their Python dependencies.

## Experiment figures and tables

- Establish row meaning, metric direction, denominators, repeated runs, timeouts, and missing values from the experiment definition. Ask when a missing definition affects the result.
- Do not introduce hypothesis tests simply because a statistical skill is installed.
- Figures and tables for the same comparison should use the same computed statistics and selection rules. Retain source paths and the configuration needed to rerun them.
- For LaTeX tables, first inspect existing project capabilities; the selected skills do not supply a dedicated table-export tool. Do not add a dependency without authorization.
- Inspect exported figures at the intended paper size. Distinguish completed checks from checks that were not run.
- For ICPC manuscript editing or submission requirements, use the existing `icpc-2027-paper` skill; generic visualization guidance does not replace venue rules.
