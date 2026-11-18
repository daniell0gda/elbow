---
name: elbow-release
description: Releases elbow - checks what changed since the last tag, runs the tests and the release build, updates the readme, the agent skill and the previews, bumps the version, tags vX.Y.Z so CI builds the Linux and Windows binaries, writes the release notes and reinstalls the local elbow binary. Use when the user asks to release or publish elbow.
---

# Release elbow

A `v*` tag makes CI test, build the Linux binary, create the GitHub release, and then build and upload the
Windows binary. Run every command from this repo's root.

## Workflow

1. See what the release holds: `git status`, `git describe --tags --abbrev=0` for the last tag, and
   `git log --oneline <last tag>..HEAD`. Commit or stash uncommitted work first.
2. Build: `python3 .claude/skills/elbow-release/scripts/test-build.py`. It runs the tests and the release build
   (with `vcvars64` on Windows). Every test must pass.
3. Update the docs when users can see the change: the kind table and input fields in `README.md`, the kinds,
   view fields and parameters in `skills/elbow-diagram/` (agents draw from it), and the previews
   (`target/release/elbow tests/<name>.json --best --out docs/previews/<name>.svg`). Look at a new preview
   before adding it. Commit as `docs: ...`.
4. Choose the version with the user: `feat` commits raise the minor version (0.2.0 -> 0.3.0), only `fix` commits
   raise the patch. Set it in `Cargo.toml` and run `test-build.py` again: it refreshes `Cargo.lock`, and CI
   builds with `--locked`, so a stale lock fails the release. Commit both files as `chore: release X.Y.Z`.
5. Ask the user before you push, then push `main`, create and push the tag, and wait for the run:

   ```bash
   git push origin main
   git tag -a vX.Y.Z -m "elbow vX.Y.Z"
   git push origin vX.Y.Z
   gh run list --limit 1
   gh run watch <run id> --exit-status
   ```

6. CI writes only a changelog link. Write the notes from the template below into a scratch file and set them:
   `gh release edit vX.Y.Z --notes-file <file>`.
7. Reinstall the local binary that other tools on this machine use. On Windows it needs `vcvars64`, like
   `test-build.py`: `cargo install --git https://github.com/daniell0gda/elbow --tag vX.Y.Z --locked --force`.

## Rules

- elbow is a library: write each commit message for its users, because the release notes come from them. Say
  what changes in the drawing or the input, never internal names. Example:
  `fix: keep sequence participants in the order they were named`.
- No `Co-Authored-By`, `Claude-Session` or other attribution lines in commits or release notes.
- Never move a tag or force-push: a published tag is final. Fix a bad release with the next patch version.

## Release notes template

```markdown
{One sentence: what this release gives a user.}

## Assets

- `elbow-vX.Y.Z-x86_64-pc-windows-msvc.zip`: the `elbow.exe` binary for Windows x86_64, with README and LICENSE.
- `elbow-vX.Y.Z-x86_64-unknown-linux-gnu.tar.gz`: the `elbow` binary for Linux x86_64 (glibc), with README and LICENSE.
- `resvg-v0.48.1-linux-x86_64.tar.gz`: the upstream resvg 0.48.1 binary for Linux x86_64, to rasterize elbow SVG output to PNG. Built by [linebender/resvg](https://github.com/linebender/resvg).

On macOS, install from the tag: `cargo install --git https://github.com/daniell0gda/elbow --tag vX.Y.Z --locked`.

## Highlights

- {One line for each user-visible change, newest kinds and fixes first.}
```

Check the resvg version against `RESVG_VERSION` in `.github/workflows/release.yml`.

## Files

- `scripts/test-build.py`: `cargo test` and `cargo build --release`, with `vcvars64` on Windows.
