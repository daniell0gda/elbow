#!/usr/bin/env python3
"""Build one HTML page from a folder of elbow views.

The folder holds page.html (the frame, with one `<!-- elbow:NAME -->` marker per diagram) and one NAME.json view
per marker. Each view is rendered with `elbow --best` into NAME.svg, its marker is replaced by that SVG, and the
page is written next to the folder as <folder>.html. Prints each diagram's report and exits with code 1 when a
view breaks a connector rule or a marker and a view do not match.

usage: python elbow_page.py <folder> [--theme light|dark] [--elbow <path to elbow>]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MARKER = re.compile(r"<!-- elbow:([\w.-]+) -->")
WIDE = 1400
INSTALL = "cargo install --git https://github.com/daniell0gda/elbow --locked"


def render(elbow: str, view: Path, theme: str) -> tuple[str, dict]:
    svg = view.with_suffix(".svg")
    command = [elbow, str(view), "--best", "--params", json.dumps({"theme": theme}), "--out", str(svg), "--report"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(f"{view.name}: {result.stderr.strip()}")
    return svg.read_text(encoding="utf-8"), json.loads(result.stderr)


def describe(name: str, report: dict) -> list[str]:
    measures = report["measures"]
    lines = [f"{name}: {len(report['violations'])} violations, {measures['crossings']} crossings, "
             f"{report['width']:g}x{report['height']:g}"]
    lines += [f"  rule {violation['rule']}: {violation['detail']}" for violation in report["violations"]]
    if report["width"] > WIDE:
        lines.append(f"  wider than {WIDE}px: the page shrinks it; cut the longest chain or split the view")
    return lines


def build(folder: Path, elbow: str, theme: str) -> bool:
    page = (folder / "page.html").read_text(encoding="utf-8")
    clean = True
    for view in sorted(folder.glob("*.json")):
        marker = f"<!-- elbow:{view.stem} -->"
        if marker not in page:
            print(f"{view.stem}: page.html has no {marker}")
            clean = False
            continue
        svg, report = render(elbow, view, theme)
        page = page.replace(marker, svg)
        print("\n".join(describe(view.stem, report)))
        clean = clean and not report["violations"]
    for name in MARKER.findall(page):
        print(f"{name}: the marker has no {name}.json")
        clean = False
    out = folder.parent / f"{folder.name}.html"
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}")
    return clean


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one HTML page from a folder of elbow views.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--theme", choices=("light", "dark"), default="light")
    parser.add_argument("--elbow", help="path to the elbow binary (default: elbow on PATH)")
    args = parser.parse_args()
    elbow = args.elbow or shutil.which("elbow")
    if not elbow:
        print(f"elbow is not on PATH. Install it: {INSTALL}", file=sys.stderr)
        return 2
    return 0 if build(args.folder, elbow, args.theme) else 1


if __name__ == "__main__":
    sys.exit(main())
