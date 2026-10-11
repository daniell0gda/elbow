# elbow for agents

elbow draws editorial diagrams as SVG from a small JSON view. See [README.md](README.md).

## Drawing diagrams

Follow [skills/elbow-diagram/SKILL.md](skills/elbow-diagram/SKILL.md). It is an Agent Skill (a `SKILL.md` with
`name` and `description`, plus scripts and references), so it also works when copied into an agent's skills
folder.

## Working on elbow

- Test with `cargo test --release`; every reference view in `tests/` must render without a rule violation.
- The code is developed in the `elbow/` folder of transcript-app and synced here. Make code changes there;
  this repo adds only the readme, the license, `docs/`, `skills/`, `.claude/` and the release workflow.
- Releases follow [.claude/skills/elbow-release/SKILL.md](.claude/skills/elbow-release/SKILL.md).
