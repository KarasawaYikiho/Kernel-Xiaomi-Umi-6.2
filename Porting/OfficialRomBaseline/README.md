# Official ROM Baseline Assets

This directory stores repository-side baseline metadata derived from the official Xiaomi UMI ROM.

The purpose of these files is to make ROM alignment reproducible inside CI without redefining the project goal away from the 6+ source kernel baseline.

## Rules

- Treat the official ROM as a validation baseline and extraction reference.
- Do not treat these files as kernel source input.
- Keep large proprietary payloads out of git unless there is a concrete need.
- Prefer metadata, hashes, header hints, and compact validation inputs.
- Keep repository filenames in title-case form while preserving canonical Android lowercase names for package-relative lookups and generated artifacts.

## Files

- `Manifest.json` — pinned ROM package metadata and key image hashes
- `BootImageBaseline.env` — shell-friendly boot image alignment hints
- `Dtbo.img` — repository-local DTBO baseline used for alignment evidence
- `Vbmeta.img` — repository-local vbmeta baseline used for alignment evidence
- `VbmetaSystem.img` — repository-local vbmeta_system baseline used for alignment evidence

`boot.img` is intentionally not checked into git because the stock image exceeds GitHub's file size limit. Its pinned size, hash, and header hints are stored in `Manifest.json` and `BootImageBaseline.env`, while local workflows can still consume a local ROM zip or extracted ROM directory.

For GitHub Actions and other environments that cannot access local ROM directories, the official `boot.img` is stored in git as split chunks under `BootImgParts/`. Repeated zero-filled chunks are represented once and mapped through `Manifest.json`; CI reconstructs the full image via `Porting/Tools/MaterializeOfficialBootImg.py`.

When you need a stock boot baseline, prefer this order:

1. `OFFICIAL_ROM_ZIP`
2. `OFFICIAL_BOOTIMG_PATH`
3. `OFFICIAL_ROM_DIR`
4. Local non-git `Porting/OfficialRomBaseline/boot.img`
5. `ROM_BOOTIMG_PATH` in `BootImageBaseline.env`
6. Reconstructed `Porting/OfficialRomBaseline/BootImgParts/` chunks

## Current Binary Inputs

The repository currently carries only compact official ROM baseline binaries for release-chain alignment:

- `Dtbo.img`
- `Vbmeta.img`
- `VbmetaSystem.img`

Workflow inputs or local extracted ROM directories are still supported, but repo-local baseline files now provide a stable fallback for CI and local validation.

For local work, prefer `OFFICIAL_ROM_DIR` or `OFFICIAL_BOOTIMG_PATH` so the official `boot.img` stays outside git while scripts can still consume it directly.

To refresh the split baseline after updating the local stock image:

```powershell
powershell -ExecutionPolicy Bypass -File "Porting/Tools/RefreshOfficialBootImgParts.ps1"
```
