# Porting Changelog

## 2026-03-08
- 初始化 5+ 移植工程骨架。
- 新增 `PORTING_PLAN.md`。
- 新增 `tools/porting/fetch_inventory.py` 用于对比 SO-TS 与 5+ 候选基线目录能力。
- 生成 `porting/inventory.json` 作为第一版清单。
- 启动 Phase 2：新增 `tools/porting/phase2_apply.sh`（defconfig + dts 首批迁移脚本）。
- 新增 Action：`.github/workflows/phase2-port-umi.yml`（自动执行迁移并尝试编译 5+ 内核）。
