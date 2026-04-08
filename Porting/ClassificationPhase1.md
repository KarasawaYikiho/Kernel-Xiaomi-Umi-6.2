# Phase 1 Classification (SO-TS 4.19 -> 5+)

Based on:

- `Porting/Inventory.json`
- `Porting/GapReport.md`

## A. Directly Portable First

1. `umi_defconfig` baseline for minimum compilable setup
2. `arch/arm64/boot/dts/vendor/*` files directly related to `sm8250`/`xiaomi`/`umi` (point-to-point migration)
3. Non-driver build orchestration logic (artifact collection, manifests, packaging skeleton)

## B. Portable With Adaptation

1. Display/audio/camera paths from old `techpack` layout
2. MIUI feature toggles and patch semantics requiring Kconfig remapping
3. Legacy DTS properties that need rename/removal in 5+ tree

## C. Not Directly Portable

1. 4.19-only private interfaces or removed APIs
2. Old vendor hacks strongly coupled to legacy frameworks

## Conclusion

- Phase2 should prioritize Class A to stabilize compile and packaging loops.
- Class B/C should be migrated subsystem-by-subsystem with explicit validation gates.
