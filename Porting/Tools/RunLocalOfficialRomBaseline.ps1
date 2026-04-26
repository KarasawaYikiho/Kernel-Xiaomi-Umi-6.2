param(
    [string]$OfficialRomDir = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($OfficialRomDir)) {
    $configLines = python "Porting/Tools/ExportPortConfig.py"
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

python "Porting/Tools/AnalyzeOfficialRomPackage.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

bash "Porting/Tools/PrepareReleaseBootimg.sh"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python "Porting/Tools/ValidateBootImage.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Local official ROM baseline prepared from: $OfficialRomDir"
Write-Host "Review: artifacts/bootimg-build.txt and artifacts/bootimg-info.txt"
