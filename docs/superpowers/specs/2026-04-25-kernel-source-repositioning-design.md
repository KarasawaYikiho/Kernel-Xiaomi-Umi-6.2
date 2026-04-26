# Kernel Source Repositioning Design

## Goal

Convert this repository from a porting orchestrator into a modified Xiaomi SM8250 kernel source tree based on `yefxx/xiaomi-umi-linux-kernel`, while retaining the existing ROM-alignment and migration evidence tooling.

## Repository Model

The repository root is the Linux kernel source root. Kernel directories such as `arch/`, `drivers/`, `include/`, `kernel/`, `fs/`, `mm/`, `net/`, `scripts/`, and `tools/` live at the top level. Existing project-specific assets remain in place under `.github/`, `Porting/`, and `Porting/Tools/`.

`yefxx/xiaomi-umi-linux-kernel` is the source baseline. SO-TS 4.19 is a reference input for device configuration, DTS intent, and driver migration clues. The official Xiaomi ROM is a validation baseline for boot image, DTBO, vbmeta, partition, and runtime expectations; it is not a code donor.

## CI Model

GitHub Actions build the checked-out repository. They no longer clone yefxx into `kernel/` or `target/`. The active kernel source is addressed by `KERNEL_DIR`, defaulting to the workspace root. SO-TS is cloned only into `REFERENCE_DIR`, defaulting to `source/`.

Generated state remains disposable:

- `out/` contains Kbuild output.
- `artifacts/` contains build reports, AnyKernel candidates, boot image validation, and phase reports.
- `artifacts/phase2/` contains migration evidence logs.

## Path Contract

Scripts use these variables consistently:

```bash
KERNEL_DIR="${KERNEL_DIR:-$PWD}"
REFERENCE_DIR="${REFERENCE_DIR:-$PWD/source}"
PHASE2_PORT_DIR="${PHASE2_PORT_DIR:-$PWD/artifacts/phase2}"
OUT_DIR="${OUT_DIR:-$PWD/out}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-$PWD/artifacts}"
```

## Migration Strategy

The first build milestone is not full device usability. It is a reproducible Phase 2 artifact where `umi_defconfig`, `Image.gz`, modules, and the initial Umi DTB build from the in-repo kernel source.

The initial `umi_defconfig` starts from the yefxx arm64 `defconfig` and incorporates only 6.11-valid, boot-relevant SO-TS intent. The initial Umi DTS follows yefxx/mainline SM8250 conventions and uses SO-TS Umi DTS files as reference, not as a blind copy.

Driver migration is staged after the build chain is stable. Boot-chain drivers come first, then Android userspace compatibility, then usability drivers, then camera.

## Non-Goals

- Do not preserve the full yefxx commit history.
- Do not keep the old external `target/` clone as the default build model.
- Do not copy SO-TS techpack subtrees wholesale.
- Do not start real-device validation before Phase 2 and the required Phase 3 gates are complete.
