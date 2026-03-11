# Phase 1 Classification (SO-TS 4.19 -> 5+)

Based on:
- `Porting/Inventory.json`
- `Porting/Gap-Report.md`

## A. 可直接移植（先做）

1. `umi_defconfig`（先落地最小可编译配置）
2. `arch/arm64/boot/dts/vendor/qcom` 中 **sm8250-xiaomi / umi 直接相关** dts/dtsi（点对点迁移）
3. 构建脚本中的非驱动逻辑（产物收集、清单生成、打包结构）

## B. 需改写后移植（中期）

1. `techpack/display`、`techpack/audio`、`techpack/camera*`：
   - 5+ 基线无同构 `techpack`，需映射到 5+ 驱动目录结构
2. MIUI 特性开关与 patch（Kconfig/符号依赖需重解）
3. 某些面板/电源节点属性（旧字段在 5+ 可能已重命名或弃用）

## C. 暂不可直接移植（后置评估）

1. 4.19 特有私有接口、已删除 API
2. 强耦合旧内核框架的 vendor hack（需重写或替代）

## 结论

- Phase 2 优先走 A 类（保证“可编译 + umi 聚焦产物”）
- B/C 类分 subsystem 渐进推进，避免一次性大爆炸式合并
