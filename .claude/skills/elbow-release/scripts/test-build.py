#!/usr/bin/env python3
"""Runs elbow's tests and release build, or installs a released elbow, with cargo.

On Windows it loads the MSVC linker environment (vcvars64) of the newest Visual Studio with C++ build tools.
The build also refreshes Cargo.lock after a version bump, which the release CI needs for --locked.
On success it prints only the result lines; on failure it prints the full cargo output.

Usage (from the repo root):
    python3 .claude/skills/elbow-release/scripts/test-build.py [--repo <checkout>]
    python3 .claude/skills/elbow-release/scripts/test-build.py --install vX.Y.Z
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = Path(__file__).resolve().parents[4]
REPO_URL = "https://github.com/daniell0gda/elbow"
RESULT_LINE = re.compile(r"^test result|FAILED|panicked|^error|^warning|^\s*Finished|^\s*Installed|^\s*Replaced")
VSWHERE_UNDER_PROGRAM_FILES = Path("Microsoft Visual Studio/Installer/vswhere.exe")
VCVARS_UNDER_VS_INSTALLATION = Path("VC/Auxiliary/Build/vcvars64.bat")
MSVC_TOOLS_COMPONENT = "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run cargo test and cargo build --release for elbow.")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="elbow checkout (default: this repo)")
    parser.add_argument("--install", metavar="TAG", help="instead, cargo install elbow from this release tag")
    return parser.parse_args()


def cargo_commands(arguments: argparse.Namespace) -> list[list[str]]:
    if arguments.install:
        return [["cargo", "install", "--git", REPO_URL, "--tag", arguments.install, "--locked", "--force"]]
    manifest = str(arguments.repo.resolve() / "Cargo.toml")
    return [
        ["cargo", "test", "--release", "--manifest-path", manifest],
        ["cargo", "build", "--release", "--manifest-path", manifest],
    ]


def find_vcvars() -> Path | None:
    vswhere = Path(os.environ.get("ProgramFiles(x86)", "")) / VSWHERE_UNDER_PROGRAM_FILES
    if not vswhere.is_file():
        return None
    query = [str(vswhere), "-latest", "-products", "*", "-requires", MSVC_TOOLS_COMPONENT, "-property", "installationPath"]
    installation = subprocess.run(query, stdout=subprocess.PIPE, text=True).stdout.strip()
    if not installation:
        return None
    vcvars = Path(installation) / VCVARS_UNDER_VS_INSTALLATION
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


def run_cargo(commands: list[list[str]]) -> subprocess.CompletedProcess[str]:
    if os.name != "nt":
        return run_in_sequence(commands)
    vcvars = find_vcvars()
    if vcvars:
        return run_in_vcvars(vcvars, commands)
    print("vcvars64 not found: cargo runs without the MSVC linker environment", file=sys.stderr)
    return run_in_sequence(commands)


def print_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        print(result.stdout, flush=True)
        print(f"cargo failed with exit code {result.returncode}", file=sys.stderr)
        return
    for line in result.stdout.splitlines():
        if RESULT_LINE.search(line):
            print(line)


def main() -> int:
    arguments = parse_arguments()
    if not shutil.which("cargo"):
        print("cargo not found on PATH: install Rust from https://rustup.rs", file=sys.stderr)
        return 1
    result = run_cargo(cargo_commands(arguments))
    print_result(result)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
