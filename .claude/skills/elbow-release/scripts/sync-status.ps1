# Shows how this repo relates to the elbow\ folder of the source repo, where elbow is developed, and exports the
# source commits this repo does not have yet as patches. Read-only for both repos; writes patches only into
# .gen\elbow-release\patches.
# Usage (from the repo root):  & .claude\skills\elbow-release\scripts\sync-status.ps1 -Source <source repo>
# Without -Source, the ELBOW_SOURCE environment variable names the source repo.
param([string]$Source = $env:ELBOW_SOURCE)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
if (-not $Source) { throw 'Name the source repo: -Source <path> or the ELBOW_SOURCE environment variable.' }
$Source = (Resolve-Path $Source).Path
$repoOnly = '^(README\.md|AGENTS\.md|LICENSE|\.gitignore|\.github/|\.claude/|bench/|docs/|skills/)'
$patches = Join-Path $root '.gen\elbow-release\patches'

function Get-Blobs([string]$repo, [string]$rev, [string]$prefix) {
    $lines = if ($prefix) { git -C $repo ls-tree -r $rev -- $prefix } else { git -C $repo ls-tree -r $rev }
    $lines | ForEach-Object {
        $meta, $path = $_ -split "`t", 2
        if ($prefix) { $path = $path.Substring($prefix.Length + 1) }
        if ($path -notmatch $repoOnly) { ($meta -split ' ')[2] + ' ' + $path }
    } | Sort-Object
}

function Get-Version([string]$manifest) {
    ([regex]::Match((Get-Content $manifest -Raw), '(?m)^version = "([^"]+)"')).Groups[1].Value
}

$published = (Get-Blobs $root 'HEAD' '') -join "`n"
$synced = $null
$unsynced = @()
foreach ($commit in git -C $Source log --format=%H -- elbow) {
    if (((Get-Blobs $Source $commit 'elbow') -join "`n") -eq $published) { $synced = $commit; break }
    $unsynced += $commit
}
if (-not $synced) { throw "No commit in $Source has the same elbow code as this repo's HEAD; sync by hand." }

Write-Host "elbow repo:      $root ($(git -C $root status --short --branch | Select-Object -First 1))"
Write-Host "source repo:     $Source"
Write-Host "last synced:     $(git -C $Source log -1 --format='%h %s' $synced)"
Write-Host "latest tag:      $(git -C $root describe --tags --abbrev=0 2>$null)"
Write-Host "versions:        source $(Get-Version (Join-Path $Source 'elbow\Cargo.toml')), elbow repo $(Get-Version (Join-Path $root 'Cargo.toml'))"
$dirtySource = git -C $Source status --porcelain -- elbow
$dirtyRepo = git -C $root status --porcelain
if ($dirtySource) { Write-Host "uncommitted in the source repo's elbow folder:`n$($dirtySource -join "`n")" }
if ($dirtyRepo) { Write-Host "uncommitted in the elbow repo:`n$($dirtyRepo -join "`n")" }

if (-not $unsynced) {
    Write-Host "in sync: this repo has every committed change of the source repo's elbow folder"
    return
}
[array]::Reverse($unsynced)
Write-Host "unsynced source commits ($($unsynced.Count)), oldest first:"
$unsynced | ForEach-Object { Write-Host "  $(git -C $Source log -1 --format='%h %s' $_)" }
New-Item -ItemType Directory -Force $patches | Out-Null
Get-ChildItem $patches -Filter *.patch | Remove-Item
git -C $Source format-patch --quiet --relative=elbow -o $patches "$synced..$($unsynced[-1])" -- elbow
Write-Host "patches:         $patches"
Get-ChildItem $patches -Filter *.patch | ForEach-Object { Write-Host "  $($_.Name)" }
