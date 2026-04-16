param(
    [string]$OfficialRomDir = 'D:\GIT\MIUI_UMI'
)

$ErrorActionPreference = 'Stop'

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
