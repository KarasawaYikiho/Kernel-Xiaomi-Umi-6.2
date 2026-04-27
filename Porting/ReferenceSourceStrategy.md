# Reference Source Strategy

## Decision

yefxx 6.11 remains the experimental mainline build baseline for this repository. It is not treated as proof that a complete Umi vendor feature stack is already available.

The 4.19 SM8250 sources and N0Kernel package are reference inputs for targeted comparison, not whole-tree replacement sources. No blind subtree copy is allowed.

## Boot Artifact Policy

The boot target is an official-aligned custom boot artifact. It should preserve the official boot image compatibility envelope while replacing the kernel payload and associated DTB inputs only when those inputs are validated.

The artifact must remain patcher-agnostic and compatible with KernelSU, Magisk, or equivalent patchers. A patcher may be used by the tester, but repository readiness must not depend on a Magisk-only or KernelSU-only path.

The first device route remains temporary `fastboot boot`; do not flash on the first pass.

## Registered References

### LineageOS/android_kernel_xiaomi_sm8250

- Role: targeted donor candidate.
- Kernel: 4.19.325.
- Value: Umi config, Umi DTS/DTSI, camera sensor DTS, and Xiaomi SM8250 techpack structure.
- Use for: Phase3 camera, DTS, power, audio, and device-specific compatibility mapping.
- Constraint: keep reference changes isolated and reviewed before any import.

### liyafe1997/kernel_xiaomi_sm8250_mod

- Role: cautious targeted donor candidate.
- Kernel: 4.19.325.
- Value: Umi stock/mod config, Umi DTS, AnyKernel packaging flow, SukiSU/SUSFS-related integration examples.
- Use for: comparison against LineageOS and N0Kernel, especially packaging and Umi-specific deltas.
- Constraint: do not blindly import SukiSU, SUSFS, KPM, or mod-specific behavior into the baseline.

### N0Kernel-umi-2024-12-30_23-10-52.zip

- Role: packaging reference.
- Kernel: 4.19.246-N0kernel.
- Value: AnyKernel3 layout containing raw `Image`, `dtb`, `dtbo.img`, and boot-partition repack behavior.
- Use for: understanding third-party Umi boot packaging and official boot reuse patterns.
- Constraint: it is not a source tree and does not contain a ready official-aligned `boot.img`.

## yefxx Baseline Feasibility

Using yefxx 6.11 is feasible as an experimental mainline bring-up path because it builds and provides a modern kernel baseline for repository automation.

Using yefxx 6.11 as the only source of device completeness is risky because current evidence lacks the Umi 4.19 vendor camera/techpack stack and full Umi DTS coverage. Phase3 must therefore compare against the registered 4.19 references before declaring device usability.
