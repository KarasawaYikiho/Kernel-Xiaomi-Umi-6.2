param(
    [string]$OfficialRomDir = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($OfficialRomDir)) {
    $configLines = python "Tools/Porting/ExportPortConfig.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to load port config defaults"
    }

    foreach ($line in $configLines) {
        if ($line -like 'OFFICIAL_ROM_DIR_DEFAULT=*') {
            $OfficialRomDir = $line.Substring('OFFICIAL_ROM_DIR_DEFAULT='.Length)
            break
        }
    }
}

if (-not (Test-Path -LiteralPath $OfficialRomDir -PathType Container)) {
    throw "Official ROM directory not found: $OfficialRomDir"
}

$env:OFFICIAL_ROM_DIR = $OfficialRomDir

python "Tools/Porting/AnalyzeOfficialRomPackage.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

bash "Tools/Porting/PrepareReleaseBootimg.sh"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python "Tools/Porting/ValidateBootImage.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Local official ROM baseline prepared from: $OfficialRomDir"
Write-Host "Review: artifacts/bootimg-build.txt and artifacts/bootimg-info.txt"
