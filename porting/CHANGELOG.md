# Porting Changelog

## 2026-03-08
- 初始化 5+ 移植工程骨架。
- 新增 `PORTING_PLAN.md`。
- 新增 `tools/porting/fetch_inventory.py` 用于对比 SO-TS 与 5+ 候选基线目录能力。
- 生成 `porting/inventory.json` 作为第一版清单。
- 启动 Phase 2：新增 `tools/porting/phase2_apply.sh`（defconfig + dts 首批迁移脚本）。
- 新增 Action：`.github/workflows/phase2-port-umi.yml`（自动执行迁移并尝试编译 5+ 内核）。
- Phase 2.2：Action 增加 `umi-focused` 产物打包（优先 umi 严格匹配，失败则回退家族匹配），输出 `phase2-umi-focused-package.zip` 用于无刷机条件下的结构验收。
- Phase 2.3：修正 umi 过滤规则，排除 `rumi/lumia/sony/hdk/mtp` 等误命中 dtb，聚焦 sm8250-xiaomi/umi 主线目标。
- 完成 Phase 0：新增 `porting/baseline-lock.json` 与 `porting/BRANCHING.md`。
- 完成 Phase 1：新增 `porting/classification-phase1.md`，并将盘点与分类结论固化。
- Phase 2.1：修复 dts 迁移逻辑（递归扫描 + 目标路径映射 + copied_dts 清单）。
- Phase 2.1：Action 产物增加 `all_dtb_paths.txt` 与 `umi_related_dtb_paths.txt`，便于定位 umi 相关 dtb 是否落地。
