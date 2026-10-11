"""Extracts the hand-drawn diagram-design SVGs that the static benchmark compares against.

Each source page was drawn by an agent with the diagram-design skill. The pages are private, so the extracted
`<svg>` elements are committed in references/; this script shows how they were cut out. Each argument maps one
page to the names of its diagrams, in the order they appear on the page.

usage: python extract_references.py <page.html>=<name>[,<name>...] [<page.html>=<name>...]
example: python extract_references.py runner-app-lifecycle.html=runner-works,runner-breaks login.html=login
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def svgs(page: Path) -> list[str]:
    return re.findall(r"(?s)<svg.*?</svg>", page.read_text(encoding="utf-8"))


def parse(argument: str) -> tuple[Path, list[str]]:
    page, separator, names = argument.rpartition("=")
    if not separator or not page or not names:
        raise SystemExit(f"expected <page.html>=<name>[,<name>...], got {argument!r}")
    return Path(page), names.split(",")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    out = HERE / "references"
    out.mkdir(exist_ok=True)
    for page, names in map(parse, sys.argv[1:]):
        for name, svg in zip(names, svgs(page)):
            (out / f"{name}.svg").write_text(svg, encoding="utf-8")
            print(f"{name}.svg  <- {page}")


if __name__ == "__main__":
    main()
