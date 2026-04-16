param(
    [string]$OfficialBootimg = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($OfficialBootimg)) {
    $configLines = python "Tools/Porting/ExportPortConfig.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to load port config defaults"
    }

    foreach ($line in $configLines) {
        if ($line -like 'OFFICIAL_BOOTIMG_DEFAULT=*') {
            $OfficialBootimg = $line.Substring('OFFICIAL_BOOTIMG_DEFAULT='.Length)
            break
        }
    }
}

if (-not (Test-Path -LiteralPath $OfficialBootimg -PathType Leaf)) {
    throw "Official boot image not found: $OfficialBootimg"
}

python "Tools/Porting/SplitOfficialBootimg.py" --input "$OfficialBootimg"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Refreshed split boot baseline from: $OfficialBootimg"
Write-Host "Review: Porting/OfficialRomBaseline/BootImgParts and Manifest.json"
