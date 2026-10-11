---
name: elbow-release
description: Releases elbow - moves the commits from transcript-app\elbow (where elbow is developed) into this repo with library-facing messages, updates the readme and previews, bumps the version in both trees, tags vX.Y.Z so CI builds the release, writes the release notes and reinstalls the local elbow binary. Use when the user asks to release, publish or sync elbow, or to make an elbow change from the app available here.
---

# Release elbow

elbow is developed in the `elbow\` folder of transcript-app, by default the sibling folder `..\transcript-app`.
This repo is the published copy: the same code plus `README.md`, `AGENTS.md`, `LICENSE`, `docs/previews/`,
`skills/` (the `elbow-diagram` agent skill), `bench/` (the benchmark data), `.claude/` and `.github/workflows/release.yml`. A `v*` tag makes CI test, build the Linux binary, create the GitHub release, and
then build and upload the Windows binary.

Run every command from this repo's root.

## Quick start

```powershell
& .claude\skills\elbow-release\scripts\sync-status.ps1
```

It prints the last synced app commit, the unsynced ones, both versions, the latest tag and uncommitted files, and
exports the unsynced commits as patches into `.gen\elbow-release\patches`. `-AppRepo <path>` points it at
another transcript-app clone.

## Workflow

1. Run `sync-status.ps1`. Commit or stash uncommitted work in the app's `elbow\` folder first: patches carry only
   committed changes.
2. Apply each patch in order and commit it with a library-facing message (see **Rules**):

   ```powershell
   rtk git apply --index .gen\elbow-release\patches\0001-....patch
   rtk git commit -m @'
   feat: ...
   '@
   ```

   Skip a patch that only bumps the version; step 5 does that. Run `sync-status.ps1` again: it must say `in sync`.
3. Build: `& .claude\skills\elbow-release\scripts\test-build.ps1`. It runs the tests and the release build with
   `vcvars64`. Every test must pass.
4. Update the docs when users can see the change: the kind table and input fields in `README.md`, the kinds,
   view fields and parameters in `skills/elbow-diagram/` (agents draw from it), and the previews (`target\release\elbow.exe tests\<name>.json --best --out docs\previews\<name>.svg`). Look at a new
   preview before adding it. Commit as `docs: ...`.
5. Choose the version with the user: `feat` commits raise the minor version (0.2.0 -> 0.3.0), only `fix` commits
   raise the patch. Set it in `Cargo.toml` and run `test-build.ps1` again: it refreshes `Cargo.lock`, and CI
   builds with `--locked`, so a stale lock fails the release. Commit both files as `chore: release X.Y.Z`.
6. Copy `Cargo.toml` and `Cargo.lock` into the app's `elbow\` folder and commit them there as
   `chore(elbow): match the released elbow X.Y.Z`. Run `sync-status.ps1`: it must say `in sync`.
7. Ask the user before you push, then push `main`, create and push the tag, and wait for the run:

   ```powershell
   rtk git push origin main
   rtk git tag -a vX.Y.Z -m "elbow vX.Y.Z"
   rtk git push origin vX.Y.Z
   rtk gh run list --limit 1
   rtk gh run watch <run id> --exit-status
   ```

8. CI writes only a changelog link. Write the notes from the template below into a scratch file and set them:
   `rtk gh release edit vX.Y.Z --notes-file <file>`.
9. Reinstall the local binary that other tools (such as the show-me skill) use. It needs `vcvars64`, like
   `test-build.ps1`: `cargo install --git https://github.com/daniell0gda/elbow --tag vX.Y.Z --locked --force`.

## Rules

- elbow is a library: write each commit message for its users, because the release notes come from them. Say
  what changes in the drawing or the input, never app terms (sketch, Jev, drawer, window, talk) and never internal
  names. Example: `fix: keep sequence participants in the order they were named`.
- No `Co-Authored-By`, `Claude-Session` or other attribution lines in commits or release notes.
- Never move a tag or force-push: a published tag is final. Fix a bad release with the next patch version.
- Do not push transcript-app as part of a release unless the user asks.

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

- `scripts/sync-status.ps1`: status of both trees and patch export (read-only for both repos).
- `scripts/test-build.ps1`: `cargo test` and `cargo build --release` with `vcvars64`; `-Repo` picks the tree.
