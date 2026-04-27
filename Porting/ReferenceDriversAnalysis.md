# Reference Driver Analysis

Source-role context is maintained in `ReferenceSourceStrategy.md`.

## Input Summary

- SO-TS drivers scanned: `145`
- 5+ base drivers scanned: `143`
- Additional donor-reference drivers: `15`

## Delta Summary

- Reference-only buckets missing in current base: `14`
- Sample buckets: `cam_core`, `cam_cpas`, `cam_isp`, `cam_sensor_module`, `cam_sync`, `cam_utils`

## UMI Prioritization

- Primary focus bucket: `cam_sensor_module`
- Secondary sequence: `xiaomi` -> `camera/video` -> `thermal/power` -> others

## Integration Rules

1. Keep yefxx 6.11 as the experimental mainline build baseline.
2. Use SO-TS, LineageOS, liyafe, and N0Kernel only for targeted deltas and packaging evidence.
3. Require Kconfig mapping + DTS compatibility + CI gate for every imported area.
4. No blind subtree copy.
