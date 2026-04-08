# Gap Report (SO-TS 4.19 -> 5+ Base)

## Defconfig Gap

- SO-TS umi-like defconfigs: `6`
- 5+ base umi-like defconfigs: `0`
- Implication: `umi_defconfig` path must be established early in Phase2.

## DTS Focus Gap

- SO-TS qcom/xiaomi/umi related files: `200`
- 5+ base qcom/xiaomi/umi related files: `34`
- Implication: start with targeted DTS subset migration, not full-tree copy.

## Techpack Gap

- SO-TS top-level `techpack` entries: `14`
- 5+ base top-level `techpack` entries: `0`
- Implication: migrate by subsystem into 5+ layout instead of preserving legacy directory model.

## Migration Implications Summary

1. Build a compilable `umi` defconfig baseline first.
2. Migrate DTS/DTSI in focused batches with manifest-driven validation.
3. Handle display/audio/camera as adaptation work, not direct copy.
