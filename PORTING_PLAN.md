# UMI 5+ 内核移植计划（SO-TS 4.19 -> 5+）

目标：将 `SO-TS/android_kernel_xiaomi_sm8250`（4.19）中的设备功能与驱动兼容，分阶段迁移到 5+ 内核基线，并保持 GitHub Actions 持续可构建。

仓库最终目标：
- 产出 **Release 级、可直接刷入的 `boot.img`**（最终交付物，不限于候选包）。
- 相同机型（umi）在相同 workflow 输入下，可通过 Actions 稳定自助编译并产出可刷写工件。

## 参考源（GitHub）

- 功能参考（低版本）：https://github.com/SO-TS/android_kernel_xiaomi_sm8250
- 5+ 候选基线： https://github.com/yefxx/xiaomi-umi-linux-kernel

## 当前状态快照（2026-03-09）

- Phase 0：完成
- Phase 1：完成
- Phase 2：进行中（已具备自动迁移 + 自动诊断 + 候选打包）
- 当前重点：提升构建通过率与 DTB 命中质量

## 实施阶段

### Phase 0 - 基线冻结（已完成）
- [x] 锁定 5+ 基线仓库 + 分支
- [x] 建立分支策略：`port/phase-*`

### Phase 1 - 能力盘点（已完成）
- [x] 提取 SO-TS 的设备 defconfig、dts、techpack、MIUI patch 点
- [x] 提取 5+ 基线的对应能力清单
- [x] 生成“可直接移植/需改写/不可移植”分类表

### Phase 2 - 最小可启动移植（已启动）
- [x] defconfig 迁移流水线（umi，自动化脚本）
- [x] dts/dtsi 首批迁移流水线（关键文件自动筛选复制）
- [x] 编译通过 + 产出 AnyKernel zip（候选）
- [ ] 产出可直接刷入的 release 级 `boot.img`（含尺寸/分区约束校验）

### Phase 3 - 功能补齐
- [ ] 显示/刷新率相关
- [ ] 音频与传感器
- [ ] KernelSU（可选）
- [ ] MIUI 特性（按可行性迁移）

### Phase 4 - 稳定性与回归
- [ ] 日常使用回归
- [ ] 功耗/发热/稳定性对比
- [ ] 发布 release candidate

## 交付规则
- 每个阶段至少 1 次可编译提交
- 每次 push 触发 GitHub Actions
- 关键变更写入 `Porting/CHANGELOG.md`
