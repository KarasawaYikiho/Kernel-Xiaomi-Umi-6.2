# UMI Kernel Porting Plan

## Mission

Migrate Xiaomi 10 (`umi`) from SO-TS 4.19 to 5+ baseline with CI reproducibility.

## Goal

- Release-grade flashable `boot.img`
- GitHub Actions reproducibility

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

## Execution Rules

- One compilable commit per phase
- Every push requires CI evidence
- Major changes update `Porting/CHANGELOG.md`