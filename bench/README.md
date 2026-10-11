# Benchmark data

How the numbers in [docs/benchmark.md](../docs/benchmark.md) were made, with every input and output.

## Agent runs

| File | What it is |
| --- | --- |
| `make_briefs.py` | Writes `briefs/NAME.brief.txt` from `../tests/NAME.json`: the same plain-text content for both methods. |
| `briefs/` | The four briefs the agents got. |
| `agent-prompts.md` | The exact prompt of each method and how the runs were started and measured. |
| `results/agent-runs.csv` | Tokens, tool uses and duration of each of the eight runs. |
| `results/hand/` | The four pages the hand-drawing agents wrote. |
| `results/elbow/` | The four views the elbow agents wrote, and the pages elbow rendered from them. |
| `results/side-by-side.png` | Screenshots: hand-drawn on the left, elbow on the right, one diagram per row. |

To repeat a run, give a fresh agent with both skills installed the prompt from `agent-prompts.md` and record the
usage your harness reports.

## Model output

| File | What it is |
| --- | --- |
| `extract_references.py` | Cuts the `<svg>` element out of each hand-drawn source page; records where each came from. |
| `references/` | The 14 hand-drawn SVGs. Their views are in `../tests/`. |
| `static_bench.py` | Counts the tokens of each SVG and view and times `elbow --best`; prints the table. |

```
pip install tiktoken
python bench/static_bench.py
```

The token counts are deterministic. The render times depend on the machine.
