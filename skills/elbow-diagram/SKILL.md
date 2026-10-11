---
name: elbow-diagram
description: Draws editorial box-and-connector diagrams as SVG or HTML with the elbow CLI - flow, sequence, state, ER, swimlane, nested, layers, dependency, timeline, fishbone, kanban, UML class, database schema and 13 more kinds. The agent writes a small JSON view with the content; elbow does the layout, routing, labels, legend and connector-rule checks. Use when a diagram would explain how things relate (components, flows, messages, states, dependencies, data models, processes, timelines), or when asked to draw, sketch or visualize such a structure.
---

# Draw diagrams with elbow

You choose the content; elbow does all the geometry in the diagram-design editorial style. Never write or edit the
SVG yourself: change the view and render again.

## Setup

`elbow` must be on PATH; running it with no arguments prints its usage. To install it:

- Windows x86_64: download `elbow-vX.Y.Z-x86_64-pc-windows-msvc.zip` from
  https://github.com/daniell0gda/elbow/releases and put `elbow.exe` in a folder on PATH.
- Linux x86_64: download `elbow-vX.Y.Z-x86_64-unknown-linux-gnu.tar.gz` from the same page and put `elbow` on
  PATH.
- Any other OS, with Rust: `cargo install --git https://github.com/daniell0gda/elbow --locked`
  (on Windows, run it in a Visual Studio Build Tools environment).

## Workflow

1. Pick the kind for what the reader must understand: [references/kinds.md](references/kinds.md).
2. Write the view as JSON (format below), one file per diagram.
3. Render it and read the report:

   ```
   elbow view.json --best --report --out diagram.svg
   ```

   `--out diagram.html` writes a standalone page instead; without `--out` the SVG goes to stdout, and `-` reads
   the view from stdin. `--best` tries a grid of layouts and keeps the best one. `--report` prints JSON to
   stderr: `violations` (`rule`, `detail`), `measures` (`crossings`, `bends`, `ambiguous_labels`, `area`),
   `width`, `height`.
4. Fix the view until the report has no violations and at most 2 crossings: drop or merge nodes, remove edges the
   point does not need, or split it into an overview and a detail view. Above about 1400 px wide, cut the
   longest chain or split the view.
5. Deliver the `.svg` or `.html`. For several diagrams on one page, see **One page, several diagrams**.

## View

```json
{
  "title": "How a login works",
  "kind": "sequence",
  "nodes": [
    {"id": "browser", "label": "Browser (web app)", "shape": "client"},
    {"id": "api", "label": "API (Node)", "shape": "service", "focal": true}
  ],
  "edges": [
    {"source": "browser", "target": "api", "label": "POST /login", "style": "sync"},
    {"source": "api", "target": "browser", "label": "session cookie", "style": "async"}
  ],
  "groups": [{"id": "edge", "label": "Edge network", "members": ["browser"]}]
}
```

- `id`: short snake_case. Edges and group `members` refer to node ids.
- `label`: a trailing `(…)` becomes the sublabel (file, technology, detail). Some kinds read it as data; see
  [references/kinds.md](references/kinds.md).
- `shape`: `service`, `database`, `queue`, `cache`, `actor`, `external`, `client`, `state`, `decision`, `note`.
  It sets the tag (SVC, DB, QUEUE, USER, EXT, APP, …) and the fill.
- `style`: `sync` (a call, solid), `async` (dashed: events and replies), `data` (reads, writes, mounts),
  `transition` (state changes), `dependency`.
- `focal: true` on the 1–2 nodes or edges the reader must see first; they turn coral.
- `selected` (ids) and `pointed` (one id) mark nodes, edges or sections for an interactive page; every node, edge
  and section is a `[data-id]` group.
- Optional fields default to `service`, `sync` and `false`.

## Parameters

Pass them as JSON with `--params`, for example `--params '{"theme": "dark"}'`: `direction` (`right`, `down`),
`theme` (`light`, `dark`), `legend` (true or false), `node_gap`, `min_channel`, `track_gap`,
`uniform_rank_size`, `ordering_sweeps`. With `--best`, elbow may choose another direction.

## Rules

- Keep the diagram-design budget: about 9 nodes; a sequence has at most 5 lifelines and 12 messages. Above it,
  draw an overview and a detail view.
- Use the real names from the code or the conversation. Keep labels short; put detail in the sublabel.
- Use one focal element, two at most. Leave everything else plain.
- elbow does not draw `alt`/`opt`/`loop` frames in a sequence, callouts or annotations, or charts (bar, line,
  Sankey, Gantt). Say so, or draw them another way; do not fake them with extra nodes.

## One page, several diagrams

Make a folder, for example `diagrams/`, with:

- `page.html`: a copy of [assets/page.html](assets/page.html) with the placeholders filled in and one
  `<!-- elbow:NAME -->` marker where each diagram goes;
- `NAME.json`: one view for each marker.

Then build it with the script in this skill's folder:

```
python <this skill's folder>/scripts/elbow_page.py diagrams [--theme dark]
```

It renders each view with `--best`, puts each SVG inline (so the page fonts apply), writes `diagrams.html` next
to the folder and prints each diagram's report. It exits with code 1 when a view breaks a rule or a marker has no
view. For a dark page, also set `background: #2d3142; color: #f5f5f5;` and `#bfc0c0` for muted text.
