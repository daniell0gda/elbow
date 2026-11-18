#!/usr/bin/env python3
"""Runs elbow's tests and release build, and prints only the result lines.

On Windows it loads the MSVC linker environment (vcvars64) first, when Build Tools 2022 are installed.
The build also refreshes Cargo.lock after a version bump, which the release CI needs for --locked.

Usage (from the repo root): python3 .claude/skills/elbow-release/scripts/test-build.py [--repo <checkout>]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = Path(__file__).resolve().parents[4]
RESULT_LINE = re.compile(r"^test result|FAILED|panicked|^error|^warning|^\s*Finished")
VCVARS_UNDER_PROGRAM_FILES = Path("Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run cargo test and cargo build --release for elbow.")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="elbow checkout (default: this repo)")
    return parser.parse_args()


def cargo_commands(manifest: Path) -> list[list[str]]:
    return [
        ["cargo", "test", "--release", "--manifest-path", str(manifest)],
        ["cargo", "build", "--release", "--manifest-path", str(manifest)],
    ]


def find_vcvars() -> Path | None:
    if os.name != "nt":
        return None
    vcvars = Path(os.environ.get("ProgramFiles(x86)", "")) / VCVARS_UNDER_PROGRAM_FILES
    return vcvars if vcvars.is_file() else None


def run_in_vcvars(vcvars: Path, commands: list[list[str]]) -> subprocess.CompletedProcess[str]:
    chained = " && ".join(subprocess.list2cmdline(command) for command in commands)
    return subprocess.run(
        f'cmd /s /c ""{vcvars}" >nul 2>&1 && {chained}"',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run_in_sequence(commands: list[list[str]]) -> subprocess.CompletedProcess[str]:
    output = ""
    for command in commands:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output += result.stdout
        if result.returncode != 0:
            return subprocess.CompletedProcess(command, result.returncode, output)
    return subprocess.CompletedProcess(commands, 0, output)


def print_result_lines(output: str) -> None:
    for line in output.splitlines():
        if RESULT_LINE.search(line):
            print(line)


def main() -> int:
    manifest = parse_arguments().repo.resolve() / "Cargo.toml"
    if not shutil.which("cargo"):
        print("cargo not found on PATH: install Rust from https://rustup.rs", file=sys.stderr)
        return 1
    commands = cargo_commands(manifest)
    vcvars = find_vcvars()
    result = run_in_vcvars(vcvars, commands) if vcvars else run_in_sequence(commands)
    print_result_lines(result.stdout)
    if result.returncode != 0:
        print(f"cargo failed with exit code {result.returncode}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
