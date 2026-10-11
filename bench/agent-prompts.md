# Agent prompts

Each run was a fresh Claude Code `general-purpose` subagent (Claude Opus 5.5, no conversation context), started
in the background, all eight in parallel on 2026-10-11. `{name}` is the diagram; the brief is
`briefs/{name}.brief.txt`. The token count, tool uses and duration in `results/agent-runs.csv` are the values
Claude Code reported when each agent finished (`subagent_tokens`, `tool_uses`, `duration_ms`).

## Hand-drawn

```
This is a timed benchmark run: work straight through, ask no questions, and wait for no confirmation.

Draw the diagram described in <bench>/{name}.brief.txt as a standalone HTML page at <bench>/hand/{name}.html.

Draw it by hand with the `diagram-design:diagram-design` skill: load it with the Skill tool and follow it (pick
the type, load that type's reference, keep its connector rules and run its taste gate). Use the default style
tokens; skip any style-guide or confirm-before-drawing questions. Do not use elbow. Do not open the page in a
browser.

When the file is written, reply with only the word: done
```

## elbow

```
This is a timed benchmark run: work straight through, ask no questions, and wait for no confirmation.

Draw the diagram described in <bench>/{name}.brief.txt with elbow: load the `elbow-diagram` skill with the Skill
tool and follow it. Write the view to <bench>/elbow/{name}.json and render it to <bench>/elbow/{name}.html
(`elbow <view> --best --report --out <html>`). Fix the view until the report has no violations. Do not open the
page in a browser.

When the file is written, reply with only the word: done
```
