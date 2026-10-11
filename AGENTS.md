# elbow for agents

elbow draws editorial diagrams as SVG from a small JSON view. See [README.md](README.md).

## Drawing diagrams

Follow [skills/elbow-diagram/SKILL.md](skills/elbow-diagram/SKILL.md). It is an Agent Skill (a `SKILL.md` with
`name` and `description`, plus scripts and references), so it also works when copied into an agent's skills
folder.

## Working on elbow

- Test with `cargo test --release`; every reference view in `tests/` must render without a rule violation.
- This repo is the only copy of elbow: make every change here.
- Releases follow [.claude/skills/elbow-release/SKILL.md](.claude/skills/elbow-release/SKILL.md).
