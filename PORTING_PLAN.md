# UMI 5+ 内核移植计划（SO-TS 4.19 -> 5+）

目标：将 `SO-TS/android_kernel_xiaomi_sm8250`（4.19）里的设备功能与驱动兼容，分批移植到 5+ 内核基线，并保持 GitHub Actions 可持续构建。

## 参考源（GitHub）

- 功能参考（低版本）：https://github.com/SO-TS/android_kernel_xiaomi_sm8250
- 5+ 候选基线： https://github.com/yefxx/xiaomi-umi-linux-kernel

## 实施阶段

### Phase 0 - 基线冻结
- [ ] 锁定 5+ 基线仓库 + 分支
- [ ] 建立分支策略：`port/phase-*`

### Phase 1 - 能力盘点（进行中）
- [ ] 提取 SO-TS 的设备 defconfig、dts、techpack、MIUI patch 点
- [ ] 提取 5+ 基线的对应能力清单
- [ ] 生成“可直接移植/需改写/不可移植”分类表

### Phase 2 - 最小可启动移植（已启动）
- [x] defconfig 迁移流水线（umi，自动化脚本）
- [x] dts/dtsi 首批迁移流水线（关键文件自动筛选复制）
- [ ] 编译通过 + 产出 AnyKernel zip

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
- 关键变更写入 `porting/CHANGELOG.md`
