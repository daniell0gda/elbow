# Runs elbow's tests and release build with the MSVC linker environment (cargo needs vcvars64 on Windows).
# Also refreshes Cargo.lock after a version bump, which the release CI needs for --locked.
# Usage (from the repo root):  & .claude\skills\elbow-release\scripts\test-build.ps1 [-Repo ..\transcript-app\elbow]
param([string]$Repo)
$ErrorActionPreference = 'Stop'
if (-not $Repo) { $Repo = Join-Path $PSScriptRoot '..\..\..\..' }
$manifest = Join-Path (Resolve-Path $Repo).Path 'Cargo.toml'
$vcvars = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$cargo = "cargo test --release --manifest-path `"$manifest`" && cargo build --release --manifest-path `"$manifest`""
$output = if (Test-Path $vcvars) { cmd /s /c "`"$vcvars`" >nul 2>&1 && $cargo 2>&1" } else { cmd /s /c "$cargo 2>&1" }
$code = $LASTEXITCODE
$output | Select-String -Pattern '^test result|FAILED|panicked|^error|^warning|^\s*Finished' | ForEach-Object { $_.Line }
if ($code -ne 0) { throw "cargo failed with exit code $code" }
