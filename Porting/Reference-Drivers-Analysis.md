# Reference Driver Analysis (Author IDs: UtsavBalar1231 / liyafe1997(=Strawing))

This report compares additional reference repositories against the current 5+ base driver layout.

## Sources
- so_ts drivers: 145
- base_5plus drivers: 143
- utsav combined reference drivers: 15

## Driver Delta
- reference-only (missing in base): 14
- sample: cam_cdm, cam_core, cam_cpas, cam_cust, cam_fd, cam_icp, cam_isp, cam_jpeg, cam_lrme, cam_req_mgr, cam_sensor_module, cam_smmu, cam_sync, cam_utils

## UMI Integration Focus (prioritized buckets)
- focus count: 1
- focus buckets: cam_sensor_module

## Strawing Discovery
- matched public repos: 0 (no public kernel/driver repos detected at scan time)

## Actionable Integration Plan
1. Keep source of truth as `so_ts` + `base_5plus`; treat extra references as donor-only for driver ideas.
2. Prioritize buckets in this order: `xiaomi` -> `camera/video` -> `thermal/power` -> other subsystems.
3. For each borrowed driver area, require: Kconfig mapping, DTS binding compatibility, and build gate in CI.
4. Avoid blind subtree copy; port only device-required deltas and validate with runtime checklist.
