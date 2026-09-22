[CmdletBinding()]
param(
    [switch]$All,
    [string[]]$Component = @(),
    [switch]$Check,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $SkillDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$ValidComponents = @(
    "video", "douyin", "bilibili", "tiktok", "weibo", "zhihu", "youtube",
    "wechat-channels", "wechat-yuanbao", "podcast", "rss", "local-audio", "rss-download"
)

function Show-Usage {
    @"
Usage:
  .\install.ps1                         # interactive menu in a terminal; all otherwise
  .\install.ps1 -All                    # install every component
  .\install.ps1 -Component youtube,podcast # install multiple components
  .\install.ps1 -Check [-Component ...]    # check all or selected components
  .\install.ps1 -Help

Components:
  video        All supported video platforms
  douyin       Douyin video transcription
  bilibili     Bilibili video transcription
  tiktok       TikTok video transcription
  weibo        Weibo video transcription
  zhihu        Zhihu video transcription
  youtube      YouTube video transcription
  wechat-channels WeChat Channels single-video transcription
  wechat-yuanbao Isolated Tencent Yuanbao fallback for WeChat Channels
  podcast      Remote podcast/audio transcription
  rss          RSS download and transcription
  local-audio  Local audio transcription
  rss-download RSS audio download only
"@
}

if ($Help) {
    Show-Usage
    exit 0
}

if ($All -and $Component.Count) {
    throw "-All cannot be combined with -Component"
}

if (-not $All -and -not $Component.Count) {
    if ($Check -or [Console]::IsInputRedirected) {
        $All = $true
    } else {
        Show-Usage
        $answer = Read-Host "Select components (comma or space separated; use all for everything)"
        $Component = @($answer -split '[,\s]+' | Where-Object { $_ })
        if (-not $Component.Count) {
            throw "No component selected"
        }
    }
}

if ($Component.Count -eq 1 -and $Component[0] -match '[,\s]') {
    $Component = @($Component[0] -split '[,\s]+' | Where-Object { $_ })
}

if ($Component -contains "all") {
    if ($Component.Count -gt 1) {
        throw "all cannot be combined with another component"
    }
    $All = $true
    $Component = @()
}

foreach ($name in $Component) {
    if ($name -notin $ValidComponents) {
        throw "Unknown component: $name"
    }
}

if ($All) {
    $Component = @("all")
}

$NeedSenseVoice = $false
$NeedWhisper = $false
$NeedDownloaders = $false
$NeedYuanbao = $false
$Commands = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)

foreach ($name in $Component) {
    switch ($name) {
        "all" {
            $NeedSenseVoice = $true
            $NeedWhisper = $true
            $NeedDownloaders = $true
            [void]$Commands.Add("curl.exe")
            [void]$Commands.Add("ffmpeg.exe")
            [void]$Commands.Add("ffprobe.exe")
        }
        "video" {
            $NeedSenseVoice = $true
            $NeedDownloaders = $true
            [void]$Commands.Add("curl.exe")
            [void]$Commands.Add("ffmpeg.exe")
            [void]$Commands.Add("ffprobe.exe")
        }
        "douyin" {
            $NeedSenseVoice = $true
            [void]$Commands.Add("curl.exe")
            [void]$Commands.Add("ffmpeg.exe")
        }
        { $_ -in @("bilibili", "tiktok", "weibo", "zhihu", "youtube") } {
            $NeedSenseVoice = $true
            $NeedDownloaders = $true
            [void]$Commands.Add("ffmpeg.exe")
            [void]$Commands.Add("ffprobe.exe")
        }
        "wechat-channels" {
            $NeedSenseVoice = $true
            [void]$Commands.Add("ffmpeg.exe")
            [void]$Commands.Add("ffprobe.exe")
        }
        "wechat-yuanbao" { $NeedYuanbao = $true }
        { $_ -in @("podcast", "rss") } {
            $NeedWhisper = $true
            [void]$Commands.Add("curl.exe")
        }
        "local-audio" { $NeedWhisper = $true }
        "rss-download" { [void]$Commands.Add("curl.exe") }
    }
}

$missingCommands = @($Commands | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) })
if ($missingCommands.Count) {
    [Console]::Error.WriteLine("Missing system commands: $($missingCommands -join ', ')")
    [Console]::Error.WriteLine("Install FFmpeg with: winget install --id Gyan.FFmpeg --exact")
    [Console]::Error.WriteLine("curl.exe is included with current Windows 10/11; update Windows or install curl if missing.")
    exit 1
}

function Find-Python {
    $candidates = @()
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) { $candidates += ,@($py.Source, "-3") }
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) { $candidates += ,@($python.Source) }
    foreach ($candidate in $candidates) {
        if ($candidate.Count -gt 1) {
            & $candidate[0] $candidate[1] -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)"
        } else {
            & $candidate[0] -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)"
        }
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $candidate[0]; Prefix = @($candidate | Select-Object -Skip 1) }
        }
    }
    throw "Missing Python 3.9 or newer. Install it from python.org or winget."
}

function Invoke-DiscoveredPython {
    param([string[]]$Arguments)
    $python = Find-Python
    & $python.Executable @($python.Prefix) @Arguments
}

function Quote-PowerShellArgument {
    param([string]$Value)
    return "'" + $Value.Replace("'", "''") + "'"
}

$installArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $SkillDir "install.ps1"))
if ($All) {
    $installArgs += "-All"
} else {
    $installArgs += "-Component"
    $installArgs += ($Component -join ",")
}
$installCommand = "powershell " + (($installArgs | ForEach-Object { Quote-PowerShellArgument $_ }) -join " ")

if (-not (Test-Path $VenvPython)) {
    if ($Check) {
        [Console]::Error.WriteLine("Missing .venv. Install the selected components with: $installCommand")
        exit 1
    }
    Invoke-DiscoveredPython @("-c", "import sys; assert sys.version_info >= (3, 9), 'Python 3.9 or newer is required'")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Invoke-DiscoveredPython @("-m", "venv", $VenvDir)
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& $VenvPython -c "import sys; assert sys.version_info >= (3, 9), 'Python 3.9 or newer is required'"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$requirementArgs = @()
if ($NeedSenseVoice) { $requirementArgs += @("-r", (Join-Path $SkillDir "requirements\sensevoice.txt")) }
if ($NeedWhisper) { $requirementArgs += @("-r", (Join-Path $SkillDir "requirements\whisper.txt")) }
if ($NeedDownloaders) { $requirementArgs += @("-r", (Join-Path $SkillDir "requirements\downloaders.txt")) }
if ($NeedYuanbao) { $requirementArgs += @("-r", (Join-Path $SkillDir "requirements\yuanbao.txt")) }
if (-not $Check -and $requirementArgs.Count) {
    & $VenvPython -m pip install @requirementArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$checkScript = @'
import importlib
import sys
need_sensevoice, need_whisper, need_downloaders, need_yuanbao = (value == "true" for value in sys.argv[1:])
modules = []
if need_sensevoice:
    modules.extend(("funasr", "modelscope", "torch", "torchaudio"))
if need_whisper:
    modules.append("faster_whisper")
if need_downloaders:
    modules.append("yt_dlp")
if need_yuanbao:
    modules.append("websocket")
failed = []
for name in modules:
    try:
        importlib.import_module(name)
    except (ImportError, OSError) as exc:
        failed.append(f"{name}: {exc}")
if failed:
    raise SystemExit("Missing or unusable Python dependencies:\n  " + "\n  ".join(failed))
print("Selected Python dependencies: OK")
'@

$checkScript | & $VenvPython - $NeedSenseVoice.ToString().ToLowerInvariant() $NeedWhisper.ToString().ToLowerInvariant() $NeedDownloaders.ToString().ToLowerInvariant() $NeedYuanbao.ToString().ToLowerInvariant()
if ($LASTEXITCODE -ne 0) {
    [Console]::Error.WriteLine("Install or repair the selected components with: $installCommand")
    exit $LASTEXITCODE
}

if ($Commands.Count) {
    Write-Output "Selected system commands: OK ($($Commands -join ' '))"
} else {
    Write-Output "Selected system commands: none required"
}
Write-Output "Components ready: $($Component -join ' ')"
Write-Output "Run: `"$VenvPython`" `"$(Join-Path $SkillDir 'scripts\transcribe.py')`" --help"
