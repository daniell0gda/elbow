"""Compares what a model writes for a hand-drawn diagram (references/NAME.svg) with the elbow view for the same
diagram (../tests/NAME.json), and times `elbow --best` on each view.

Token counts use tiktoken o200k_base as an estimate. The view is measured as an agent writes it: only title, kind,
nodes, edges and groups, without fields that have their default value. Prints a Markdown table.

usage: python static_bench.py [--elbow <path>] [--runs 5]
requires: pip install tiktoken
"""
import argparse
import json
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

import tiktoken

HERE = Path(__file__).resolve().parent
TESTS = HERE.parent / "tests"
DEFAULTS = {"shape": "service", "style": "sync", "focal": False}
VIEW_FIELDS = ("title", "kind", "nodes", "edges", "groups")
ENCODING = tiktoken.get_encoding("o200k_base")
ORDER = ["backend", "hiring", "issue", "login", "order", "org", "runner-works", "runner-breaks", "runner-services",
         "focus-click", "focus-coupling", "compose-workers", "npm-cache", "skill-updates"]


def order(name: str) -> int:
    return ORDER.index(name) if name in ORDER else len(ORDER)


def written_view(view: dict) -> str:
    kept = {key: value for key, value in view.items() if key in VIEW_FIELDS and value != []}
    for item in kept["nodes"] + kept["edges"]:
        derived = [key for key, value in item.items() if DEFAULTS.get(key) == value or (key == "id" and "->" in str(value))]
        for key in derived:
            del item[key]
    return json.dumps(kept, indent=1, ensure_ascii=False)


def tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def render_ms(elbow: str, view: Path, runs: int) -> float:
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "diagram.svg"
        times = []
        for _ in range(runs):
            started = time.perf_counter()
            subprocess.run([elbow, str(view), "--best", "--out", str(out)], check=True, capture_output=True)
            times.append((time.perf_counter() - started) * 1000)
    return statistics.median(times)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elbow", default=shutil.which("elbow"))
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    rows = []
    for svg in sorted((HERE / "references").glob("*.svg"), key=lambda path: order(path.stem)):
        view_path = TESTS / f"{svg.stem}.json"
        view = json.loads(view_path.read_text(encoding="utf-8"))
        hand = tokens(svg.read_text(encoding="utf-8"))
        written = tokens(written_view(view))
        rows.append((svg.stem, view["kind"], hand, written, render_ms(args.elbow, view_path, args.runs)))
    print("| Diagram | Kind | Hand-drawn SVG tokens | elbow view tokens | Ratio | elbow --best (ms) |")
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for name, kind, hand, written, ms in rows:
        print(f"| {name} | {kind} | {hand:,} | {written:,} | {hand / written:.1f}x | {ms:.0f} |")
    hand_total, view_total = sum(row[2] for row in rows), sum(row[3] for row in rows)
    print(f"| **Total ({len(rows)})** | | **{hand_total:,}** | **{view_total:,}** | **{hand_total / view_total:.1f}x** | "
          f"median {statistics.median(row[4] for row in rows):.0f} |")


if __name__ == "__main__":
    main()
