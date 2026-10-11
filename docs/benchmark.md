# Benchmark: elbow against hand-drawn diagrams

Before elbow, an agent drew each diagram by hand: it loaded the diagram-design skill, planned every coordinate
and wrote the SVG itself. With elbow, the agent writes a small JSON view and elbow does the geometry. This page
compares the two on the same diagrams. Measured on 2026-10-11 with elbow v0.2.1.

## Agent runs

Eight fresh Claude Code agents (Claude Opus 5.5) each drew one diagram from the same plain-text brief: the
elements, the connections in order, and the groups. Four drew it by hand with the diagram-design skill; four
used the [elbow-diagram skill](../skills/elbow-diagram/SKILL.md). Tokens are the agent's total as the harness
reports it (its context, the skill it loaded, its reasoning and its output); time is wall time. One run each,
all eight in parallel, so expect some variance.

| Diagram | Kind | Hand-drawn tokens | Hand-drawn time | elbow tokens | elbow time | Result |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| runner-services | sequence | 81,179 | 82 s | 47,393 | 13 s | Both clean and close to each other. |
| focus-coupling | flow | 77,948 | 115 s | 47,948 | 16 s | Both clean; elbow stacks it top-down, so it is taller. |
| npm-cache | swimlane | 80,275 | 112 s | 48,737 | 16 s | Hand-drawn is cleaner; elbow has 1 crossing and a long edge across a lane. |
| compose-workers | nested | 78,677 | 129 s | 52,955 | 46 s | Hand-drawn is cleaner; elbow has 3 crossings and crowded group labels. |
| **Total** | | **318,079** | **439 s** | **197,033** | **91 s** | |

elbow used 38% fewer tokens and was 4.8 times faster. Every elbow result passed the connector rules; the
hand-drawn ones have no checker. Nested and swimlane layouts are where hand drawing still looks better.

## What the model writes

The output a model must write is the slowest part of drawing. For 14 diagrams that exist both as a hand-drawn
show-me diagram and as an elbow view, this table compares the hand-drawn `<svg>` element with the view JSON as an
agent writes it (without default fields). Tokens are counted with tiktoken `o200k_base` as an estimate.
`elbow --best` is the median of 5 runs, including process start, on Windows x86_64.

| Diagram | Kind | Hand-drawn SVG tokens | elbow view tokens | Ratio | elbow --best (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| backend | flow | 4,445 | 464 | 9.6x | 36 |
| hiring | swimlane | 2,929 | 581 | 5.0x | 25 |
| issue | swimlane | 4,246 | 671 | 6.3x | 29 |
| login | sequence | 3,752 | 344 | 10.9x | 16 |
| order | state | 3,342 | 450 | 7.4x | 26 |
| org | tree | 3,440 | 436 | 7.9x | 24 |
| runner-works | sequence | 4,669 | 527 | 8.9x | 20 |
| runner-breaks | sequence | 3,990 | 443 | 9.0x | 18 |
| runner-services | sequence | 4,301 | 459 | 9.4x | 19 |
| focus-click | sequence | 3,517 | 427 | 8.2x | 18 |
| focus-coupling | flow | 3,385 | 485 | 7.0x | 33 |
| compose-workers | nested | 5,001 | 716 | 7.0x | 41 |
| npm-cache | swimlane | 3,467 | 552 | 6.3x | 22 |
| skill-updates | swimlane | 3,396 | 547 | 6.2x | 17 |
| **Total (14)** | | **53,880** | **7,102** | **7.6x** | median 23 |

The views are in [`tests/`](../tests). The hand-drawn diagrams come from private show-me pages and are not
published.
