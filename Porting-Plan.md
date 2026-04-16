# SM8250 Kernel Porting Plan

## Mission

Migrate Xiaomi SM8250-family kernels from SO-TS 4.19 to a 5+ baseline with CI reproducibility, using `umi` as the current reference baseline.

## Goal

- Release-grade flashable `boot.img`
- GitHub Actions reproducibility

## Official ROM Alignment Principle

This project targets a 6+ kernel baseline built from source for Xiaomi SM8250-family devices, with `umi` serving as today’s reference ROM-alignment sample.

The official Xiaomi ROM is used as a reference extraction source and validation baseline for:
- `boot.img` size and packaging constraints
- `dtbo` / `vbmeta` / dynamic partition expectations
- boot-chain consistency checks
- runtime validation on official userspace

The official ROM is not the target kernel version for this repository and should not be treated as a code donor.

## References

- SO-TS: `android_kernel_xiaomi_sm8250` (4.19)
- 5+ baseline: `yefxx/xiaomi-umi-linux-kernel`
- Driver donors: `UtsavBalar1231/*`

## Phase Status

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ | Baseline lock |
| 1 | ✅ | Capability inventory |
| 2 | 🔄 In Progress | Migration + packaging |
| 3 | ⏳ | Feature completion |
| 4 | ⏳ | Stability & regression |

## Phase 2 Checklist

- [x] Automated defconfig migration
- [x] Automated DTS/DTSI seed
- [x] CI build + AnyKernel packaging
- [ ] Release-grade boot.img
- [ ] ROM-aligned boot / `dtbo` / `vbmeta` consistency checks
- [ ] Resolve DTB manifest-to-build mismatches
- [ ] Device-side runtime validation on official ROM environment

## Execution Rules

- One compilable commit per phase
- Every push requires CI evidence
- Major changes update `Porting/CHANGELOG.md`
