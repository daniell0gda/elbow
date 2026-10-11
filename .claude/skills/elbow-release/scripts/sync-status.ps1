# Shows how this repo relates to transcript-app\elbow, where elbow is developed, and exports the app commits
# this repo does not have yet as patches. Read-only for both repos; writes patches only into .gen\elbow-release\patches.
# Usage (from the repo root):  & .claude\skills\elbow-release\scripts\sync-status.ps1 [-AppRepo ..\transcript-app]
param([string]$AppRepo)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
if (-not $AppRepo) { $AppRepo = Join-Path (Split-Path $root -Parent) 'transcript-app' }
$AppRepo = (Resolve-Path $AppRepo).Path
$repoOnly = '^(README\.md|LICENSE|\.gitignore|\.github/|\.claude/|docs/)'
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
foreach ($commit in git -C $AppRepo log --format=%H -- elbow) {
    if (((Get-Blobs $AppRepo $commit 'elbow') -join "`n") -eq $published) { $synced = $commit; break }
    $unsynced += $commit
}
if (-not $synced) { throw "No commit in $AppRepo has the same elbow code as this repo's HEAD; sync by hand." }

Write-Host "elbow repo:      $root ($(git -C $root status --short --branch | Select-Object -First 1))"
Write-Host "app repo:        $AppRepo"
Write-Host "last synced:     $(git -C $AppRepo log -1 --format='%h %s' $synced)"
Write-Host "latest tag:      $(git -C $root describe --tags --abbrev=0 2>$null)"
Write-Host "versions:        app $(Get-Version (Join-Path $AppRepo 'elbow\Cargo.toml')), elbow repo $(Get-Version (Join-Path $root 'Cargo.toml'))"
$dirtyApp = git -C $AppRepo status --porcelain -- elbow
$dirtyRepo = git -C $root status --porcelain
if ($dirtyApp) { Write-Host "uncommitted in the app's elbow folder:`n$($dirtyApp -join "`n")" }
if ($dirtyRepo) { Write-Host "uncommitted in the elbow repo:`n$($dirtyRepo -join "`n")" }

if (-not $unsynced) {
    Write-Host "in sync: this repo has every committed change of the app's elbow folder"
    return
}
[array]::Reverse($unsynced)
Write-Host "unsynced app commits ($($unsynced.Count)), oldest first:"
$unsynced | ForEach-Object { Write-Host "  $(git -C $AppRepo log -1 --format='%h %s' $_)" }
New-Item -ItemType Directory -Force $patches | Out-Null
Get-ChildItem $patches -Filter *.patch | Remove-Item
git -C $AppRepo format-patch --quiet --relative=elbow -o $patches "$synced..$($unsynced[-1])" -- elbow
Write-Host "patches:         $patches"
Get-ChildItem $patches -Filter *.patch | ForEach-Object { Write-Host "  $($_.Name)" }
