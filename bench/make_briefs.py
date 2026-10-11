"""Writes the plain-text brief for each agent-run diagram from its view in ../tests, so the hand-drawing agent and
the elbow agent get exactly the same content and neither sees the other's format.

usage: python make_briefs.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE.parent / "tests"
CASES = {"runner-services": "a sequence diagram", "focus-coupling": "a component diagram",
         "npm-cache": "a swimlane diagram", "compose-workers": "an architecture diagram with nested network boundaries"}
STYLE_WORDS = {"sync": "call", "async": "async / reply (dashed)", "data": "data / mount (dashed)",
               "transition": "transition", "dependency": "dependency"}


def brief(name: str, kind_words: str) -> str:
    view = json.loads((TESTS / f"{name}.json").read_text(encoding="utf-8"))
    labels = {node["id"]: node["label"] for node in view["nodes"]}
    lines = [f"Title: {view['title']}", f"Draw it as {kind_words}.", "", "Elements (label, kind):"]
    lines += [f"- {node['label']} ({node['shape']}{', highlight it' if node.get('focal') else ''})" for node in view["nodes"]]
    lines += ["", "Connections, in order (from -> to: label, kind):"]
    lines += [f"- {labels[edge['source']]} -> {labels[edge['target']]}: {edge['label'] or '(no label)'}, "
              f"{STYLE_WORDS[edge['style']]}" for edge in view["edges"]]
    if view["groups"]:
        lines += ["", "Groups (label: members):"]
        lines += [f"- {group['label']}: {', '.join(labels[member] for member in group['members'])}" for group in view["groups"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    out = HERE / "briefs"
    out.mkdir(exist_ok=True)
    for case, words in CASES.items():
        (out / f"{case}.brief.txt").write_text(brief(case, words), encoding="utf-8")
        print(f"briefs/{case}.brief.txt")


if __name__ == "__main__":
    main()
