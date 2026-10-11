"""Extracts the hand-drawn diagram-design SVGs that the static benchmark compares against.

Each source page was drawn by an agent with the diagram-design skill (show-me pages and the sketch-eval references
of transcript-app). The show-me pages are private, so the extracted `<svg>` elements are committed in
references/; this script records where each one came from and how it was cut out.

usage: python extract_references.py [--app <transcript-app checkout>]
"""
import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOW_ME_PAGES = {
    r"P:\hermes\.gen\show-me-runner-app-lifecycle.html": ["runner-works", "runner-breaks"],
    r"P:\hermes\.gen\show-me-runner-services.html": ["runner-services"],
    r"P:\gitea\tetra\.gen\show-me-focus-pulse.html": ["focus-click", "focus-coupling"],
    r"P:\hermes\.gen\show-me-compose-and-workers.html": ["compose-workers"],
    r"P:\hermes\.gen\show-me-npm-deps-cache.html": ["npm-cache"],
    r"P:\hermes\.gen\show-me-skill-updates.html": ["skill-updates"],
}
SKETCH_EVAL = ["backend", "hiring", "issue", "login", "order", "org"]


def svgs(page: Path) -> list[str]:
    return re.findall(r"(?s)<svg.*?</svg>", page.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, default=HERE.parents[1] / "transcript-app")
    args = parser.parse_args()
    out = HERE / "references"
    out.mkdir(exist_ok=True)
    pages = {Path(page): names for page, names in SHOW_ME_PAGES.items()}
    pages.update({args.app / ".claude" / "skills" / "sketch-eval" / "references" / f"{name}.html": [name] for name in SKETCH_EVAL})
    for page, names in pages.items():
        for name, svg in zip(names, svgs(page)):
            (out / f"{name}.svg").write_text(svg, encoding="utf-8")
            print(f"{name}.svg  <- {page}")


if __name__ == "__main__":
    main()
