<#
  Codex Skills Catalog - on-demand installer  (Windows / PowerShell)

  Downloads every skill from its ORIGINAL repository and copies it into your
  Codex skills folder. This script never redistributes the files itself.

  Usage:
    .\install.ps1 -List                 # show what is available
    .\install.ps1                       # install everything
    .\install.ps1 -Only innovation-proposal,qu-ai-wei
    .\install.ps1 -Bundle open-design   # install one source pack
    .\install.ps1 -Dest "D:\CodexSkills" -Link   # store on another drive + junction

  Licences: MIT / Apache-2.0 packs may be reused freely. Skills marked
  "NONE" have no licence file upstream (personal use only), and
  lieflat-charts is PolyForm Noncommercial - do not use it commercially.
#>

param(
    [string[]]$Only,
    [string[]]$Bundle,
    [string]$Dest = (Join-Path $env:USERPROFILE ".codex\skills"),
    [string]$Manifest,
    [string]$WorkDir = (Join-Path $env:TEMP "codex-skills-install"),
    [switch]$List,
    [switch]$Link,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Manifest) {
    $Manifest = Join-Path $here "manifest.json"
    if (-not (Test-Path $Manifest)) {
        throw "manifest.json not found next to install.ps1 (pass -Manifest <path>)"
    }
}

$manifestData = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
$skills = $manifestData.skills
$bundles = $manifestData.bundles

if ($List) {
    $bundles | Sort-Object bundle | ForEach-Object {
        [pscustomobject]@{
            Pack     = $_.bundle
            Repo     = $_.repo
            Skills   = $_.skillCount
            License  = $_.license
            Reusable = if ($_.redistributable) { "yes" } else { "no" }
        }
    } | Format-Table -AutoSize
    Write-Host ("skills: {0}   packs: {1}" -f $skills.Count, $bundles.Count)
    return
}

$mirrors = @(
    "https://gh-proxy.com/https://github.com",
    "https://github.com"
)

function Get-BundleZip {
    param([string]$Repo, [string]$Ref)
    New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
    $safe = ($Repo -replace "[\\/]", "_")
    $zip = Join-Path $WorkDir "$safe-$Ref.zip"
    if (Test-Path $zip) { return $zip }
    foreach ($base in $mirrors) {
        $url = "$base/$Repo/archive/refs/heads/$Ref.zip"
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            try {
                & curl.exe -L -s --retry 2 --retry-all-errors --connect-timeout 20 --max-time 900 -o $zip $url
                if ($LASTEXITCODE -eq 0 -and (Test-Path $zip) -and (Get-Item $zip).Length -gt 1000) {
                    return $zip
                }
            } catch { }
            Start-Sleep -Seconds 2
        }
        Write-Host "  mirror failed, trying next: $base"
    }
    throw "could not download $Repo"
}

function Install-Bundle {
    param($Pack, [object[]]$Wanted)
    $zip = Get-BundleZip -Repo $Pack.repo -Ref $Pack.ref
    $extract = Join-Path $WorkDir ("x-" + ($Pack.repo -replace "[\\/]", "_"))
    if (Test-Path $extract) { [System.IO.Directory]::Delete($extract, $true) }
    Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
    $root = Get-ChildItem -LiteralPath $extract -Directory | Select-Object -First 1
    $installed = 0
    foreach ($skill in $Wanted) {
        $rel = if ($skill.repoPath) { $skill.repoPath } else { "." }
        $source = if ($rel -eq ".") { $root.FullName } else { Join-Path $root.FullName ($rel -replace "/", "\") }
        if (-not (Test-Path $source)) {
            Write-Warning ("missing in repo: {0} ({1})" -f $skill.name, $skill.repoPath)
            continue
        }
        $target = Join-Path $Dest $skill.name
        if (Test-Path $target) {
            if (-not $Force) { Write-Host ("skip  {0} (already installed)" -f $skill.name); continue }
            [System.IO.Directory]::Delete($target, $true)
        }
        if ($Link) {
            New-Item -ItemType Directory -Force -Path $Dest | Out-Null
            New-Item -ItemType Junction -Path $target -Target $source | Out-Null
        } else {
            Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
        }
        Write-Host ("install {0}" -f $skill.name)
        $installed++
    }
    return $installed
}

$selected = $skills
if ($Only) { $selected = $selected | Where-Object { $Only -contains $_.name } }
if ($Bundle) { $selected = $selected | Where-Object { $Bundle -contains $_.bundle } }
if (-not $selected) { throw "nothing selected (use -List to see available names)" }

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Write-Host ("target: {0}" -f $Dest)

$total = 0
foreach ($pack in ($bundles | Where-Object { $Bundle -or ($selected.bundle -contains $_.bundle) })) {
    $wanted = $selected | Where-Object { $_.bundle -eq $pack.bundle }
    if (-not $wanted) { continue }
    Write-Host ("`n[{0}] {1} ({2} skills, {3})" -f $pack.bundle, $pack.repo, $pack.skillCount, $pack.license)
    $total += Install-Bundle -Pack $pack -Wanted $wanted
}

Write-Host ("`ndone: {0} skills -> {1}" -f $total, $Dest)
Write-Host "restart Codex (or open a new conversation) to pick them up."
