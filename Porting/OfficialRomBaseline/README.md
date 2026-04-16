# Official ROM Baseline Assets

This directory stores repository-side baseline metadata derived from the official Xiaomi UMI ROM.

The purpose of these files is to make ROM alignment reproducible inside CI without redefining the project goal away from the 6+ source kernel baseline.

## Rules

- Treat the official ROM as a validation baseline and extraction reference.
- Do not treat these files as kernel source input.
- Keep large proprietary payloads out of git unless there is a concrete need.
- Prefer metadata, hashes, header hints, and compact validation inputs.
- Keep shipped firmware image filenames in their canonical Android lowercase form so script lookups and package-relative names stay aligned. Split helper chunks follow repository naming rules instead.

## Files

- `Manifest.json` — pinned ROM package metadata and key image hashes
- `BootImageBaseline.env` — shell-friendly boot image alignment hints
- `dtbo.img` — repository-local DTBO baseline used for alignment evidence
- `vbmeta.img` — repository-local vbmeta baseline used for alignment evidence
- `vbmeta_system.img` — repository-local vbmeta_system baseline used for alignment evidence

`boot.img` is intentionally not checked into git because the stock image exceeds GitHub's file size limit. Its pinned size, hash, and header hints are stored in `Manifest.json` and `BootImageBaseline.env`, while local workflows can still consume a local ROM zip or extracted ROM directory.

For GitHub Actions and other environments that cannot access local ROM directories, the official `boot.img` is stored in git as split chunks under `BootImgParts/`. CI reconstructs it automatically via `Tools/Porting/MaterializeOfficialBootimg.py`.

When you need a stock boot baseline, prefer this order:

1. `OFFICIAL_ROM_DIR` or `OFFICIAL_ROM_ZIP`
2. Local non-git `Porting/OfficialRomBaseline/boot.img`
3. `ROM_BOOTIMG_PATH` in `BootImageBaseline.env`
4. Workflow input `bootimg_prebuilt_path`

## Current Binary Inputs

The repository currently carries only compact official ROM baseline binaries for release-chain alignment:

- `dtbo.img`
- `vbmeta.img`
- `vbmeta_system.img`

Workflow inputs or local extracted ROM directories are still supported, but repo-local baseline files now provide a stable fallback for CI and local validation.

For local work on this machine, prefer `OFFICIAL_ROM_DIR=D:\GIT\MIUI_UMI` so the official `boot.img` stays outside git while scripts can still consume it directly.

To refresh the split baseline after updating the local stock image:

```powershell
powershell -ExecutionPolicy Bypass -File "Tools/Porting/RefreshOfficialBootimgParts.ps1"
```
