param(
  [Parameter(Mandatory=$true)]
  [string]$QuarantineRoot,

  [switch]$DeleteOriginals,

  [switch]$ForceAcl
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($QuarantineRoot)) {
  throw "QuarantineRoot is required."
}

$SourceDir = "C:\Windows\Installer"
$SourceResolved = (Resolve-Path -LiteralPath $SourceDir).Path
if (-not $SourceResolved.Equals("C:\Windows\Installer", [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Unexpected source path: $SourceResolved"
}

$quarantineFullPath = [System.IO.Path]::GetFullPath($QuarantineRoot)
if ($quarantineFullPath.StartsWith("C:\Windows", [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Choose a quarantine directory outside C:\Windows."
}

New-Item -ItemType Directory -Path $quarantineFullPath -Force | Out-Null
$Log = Join-Path $quarantineFullPath "quarantine-orphan-msp.log"
"START $(Get-Date -Format o)" | Out-File -LiteralPath $Log -Encoding UTF8

try {
  $registered = Get-ChildItem -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\*\Products\*\Patches\*' -ErrorAction SilentlyContinue |
    ForEach-Object { (Get-ItemProperty -LiteralPath $_.PsPath -ErrorAction SilentlyContinue).LocalPackage } |
    Where-Object { $_ } |
    ForEach-Object { Split-Path $_ -Leaf }

  $regSet = @{}
  foreach ($item in $registered) { $regSet[$item.ToLowerInvariant()] = $true }

  $candidates = Get-ChildItem -LiteralPath $SourceResolved -Force -File -Filter "*.msp" |
    Where-Object { -not $regSet.ContainsKey($_.Name.ToLowerInvariant()) } |
    Sort-Object Length -Descending

  $candidateManifest = Join-Path $quarantineFullPath "manifest-candidates.csv"
  $candidates |
    Select-Object FullName, Name, Length, @{Name="SizeGB"; Expression={[math]::Round($_.Length / 1GB, 4)}}, LastWriteTime |
    Export-Csv -LiteralPath $candidateManifest -NoTypeInformation -Encoding UTF8

  $candidateBytes = ($candidates | Measure-Object Length -Sum).Sum + 0
  "Candidates: $($candidates.Count), GB: $([math]::Round($candidateBytes / 1GB, 2))" | Add-Content -LiteralPath $Log

  $verified = New-Object System.Collections.Generic.List[object]
  foreach ($file in $candidates) {
    $src = (Resolve-Path -LiteralPath $file.FullName).Path
    if (-not $src.StartsWith($SourceResolved + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
      throw "Unsafe source path: $src"
    }

    $dest = Join-Path $quarantineFullPath $file.Name
    if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Force }
    Copy-Item -LiteralPath $src -Destination $dest -Force

    $destItem = Get-Item -LiteralPath $dest
    if ($destItem.Length -ne $file.Length) { throw "Size verify failed: $src -> $dest" }

    $srcHash = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash
    $destHash = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
    if ($srcHash -ne $destHash) { throw "Hash verify failed: $src -> $dest" }

    $verified.Add([PSCustomObject]@{
      Source = $src
      Destination = $dest
      Length = $file.Length
      SizeGB = [math]::Round($file.Length / 1GB, 4)
      SHA256 = $srcHash
    }) | Out-Null
  }

  $verifiedManifest = Join-Path $quarantineFullPath "manifest-verified.csv"
  $verified | Export-Csv -LiteralPath $verifiedManifest -NoTypeInformation -Encoding UTF8
  "Verified: $($verified.Count)" | Add-Content -LiteralPath $Log

  if (-not $DeleteOriginals) {
    "DRY RUN: Originals were not deleted. Re-run with -DeleteOriginals only after explicit approval." | Add-Content -LiteralPath $Log
    "END OK $(Get-Date -Format o)" | Add-Content -LiteralPath $Log
    return
  }

  $deleted = New-Object System.Collections.Generic.List[object]
  foreach ($item in $verified) {
    $src = $item.Source
    if (-not (Test-Path -LiteralPath $src)) { continue }
    if (-not $src.StartsWith($SourceResolved + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
      throw "Unsafe delete path: $src"
    }

    if ($ForceAcl) {
      $takeown = Start-Process -FilePath takeown.exe -ArgumentList @("/F", $src, "/A") -Wait -PassThru -WindowStyle Hidden
      if ($takeown.ExitCode -ne 0) { throw "takeown failed $($takeown.ExitCode): $src" }

      $icacls = Start-Process -FilePath icacls.exe -ArgumentList @($src, "/grant", "Administrators:F") -Wait -PassThru -WindowStyle Hidden
      if ($icacls.ExitCode -ne 0) { throw "icacls failed $($icacls.ExitCode): $src" }
    }

    Remove-Item -LiteralPath $src -Force
    $deleted.Add($item) | Out-Null
  }

  $deletedManifest = Join-Path $quarantineFullPath "manifest-deleted.csv"
  $deleted | Export-Csv -LiteralPath $deletedManifest -NoTypeInformation -Encoding UTF8
  $deletedBytes = ($deleted | Measure-Object Length -Sum).Sum + 0
  "Deleted: $($deleted.Count), GB: $([math]::Round($deletedBytes / 1GB, 2))" | Add-Content -LiteralPath $Log
  "END OK $(Get-Date -Format o)" | Add-Content -LiteralPath $Log
} catch {
  "ERROR $($_.Exception.Message)" | Add-Content -LiteralPath $Log
  throw
}
