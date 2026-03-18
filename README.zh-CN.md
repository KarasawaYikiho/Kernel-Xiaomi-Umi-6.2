# Kernel-Xiaomi-Umi

[English README](./README.md)

Kernel-Xiaomi-Umi 是一个面向 Xiaomi 10（`umi`）内核迁移的**编排仓库**，核心目标是把迁移流程、诊断流程和交付流程做成可复现的 CI 自动化。

> 本仓库**不是**完整内核源码仓库。

## 仓库职责

- 运行基于 GitHub Actions 的迁移/构建流程
- 执行 SO-TS 4.19 -> 5+ 基线的 Phase2 迁移
- 产出结构化诊断（`phase2-report`、`next-focus`、metrics、一致性校验）
- 产出候选包与 Release 导向的 `boot.img` 就绪信号

## 最终交付目标

1. 生成 **Release 级、可直接刷入的 `boot.img`**（面向 `umi`）。
2. 保证 **同机型 + 同输入的 Actions 可复现性**。
3. 每次运行都保留完整诊断证据链（报告、错误摘要、指标、验证清单）。

## 参考源策略

- SO-TS 参考源：<https://github.com/SO-TS/android_kernel_xiaomi_sm8250>
- 补充驱动参考：
  - `UtsavBalar1231/android_kernel_xiaomi_sm8150`
  - `UtsavBalar1231/display-drivers`
  - `UtsavBalar1231/camera-kernel`
  - `liyafe1997`（Strawing，作者 ID 发现源）

规则：
- 作者 ID 仅用于发现，实际集成前必须明确到具体仓库。
- 参考源仅用于定向迁移/对比，不允许整树盲拷贝。
- 不向仓库导入官方 ROM 专有 blob。

## 官方 ROM 基线（仅分析）

- 基线包：`D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip`
- 分析文档：`Porting/OfficialRom-Umi-Os1.0.5.0-Analysis.md`
- 分析范围：metadata/hash/partition-op 证据，不含 blob 导入

## 主要工作流

> CI 兼容说明：工作流设置 `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`。

### 快速开始（推荐）

先运行 **`Phase2-Port-Umi.yml`** 默认参数，然后按顺序查看：

1. `artifacts/runtime-validation-summary.md`
2. `artifacts/runtime-validation-input.md`
3. `artifacts/runtime-validation-result.txt`
4. `artifacts/phase2-report.txt`
5. `artifacts/status-badge-line.txt`
6. `artifacts/action-validation-checklist.md`
7. `artifacts/artifact-summary.md`
8. `artifacts/next-focus.txt`
9. `artifacts/build-error-summary.txt`
10. `artifacts/anykernel-info.txt`

Runtime gate 说明：
- `driver_integration_status=partial` **不一定**阻塞实机验证。
- 如果 `next_action=ready-for-action-test` 且 `runtime_ready=yes`，则剩余的 `driver_integration_pending` 默认按 Release / ROM 对齐后续项处理，除非它们被明确列进 runtime blocker。

### `Phase2-Port-Umi.yml`

核心迁移流水线，包含：

1. 依赖与工具准备
2. source/target 拉取
3. Phase2 迁移应用
4. 构建尝试
5. 工件收集与打包
6. 报告/指标/一致性/清单后处理

关键输入：

- `device`（默认 `umi`）
- `source_repo` / `target_repo`
- `bootimg_ramdisk_url`（可选）
- `bootimg_prebuilt_url`（可选回退）
- `bootimg_required_bytes`（默认 `134217728`，设为 `<=0` 可关闭尺寸校验）

实机验证后：
- 填写 `artifacts/runtime-validation-input.md`
- 重新执行 postprocess，即可自动生成 `runtime-validation-result.txt` 并刷新 `phase2-report / next-focus / badge / summary`
- 如果实机验证 PASS，决策流会自动从 `ready-for-action-test` 切到 Release 收口（`prepare-release-bootimg`）或剩余 ROM / driver 对齐收尾（`integrate-drivers-phase3`）
- 若本地改动了决策语义，Push 前建议执行 `python Tools/Porting/Selftest_Decision_Flow.py`

### `Build-Umi-Kernel.yml`

参考式云端构建流程：

1. 安装依赖与 ccache
2. 获取工具链
3. 克隆目标仓库
4. 运行 `build.sh`
5. 上传构建产物

## 文档索引

- `PORTING_PLAN.md`：路线图与阶段状态
- `Porting/README.md`：迁移文档索引
- `Tools/Porting/README.md`：脚本与 CI 流程索引
- `CONTRIBUTING.zh-CN.md`：贡献规范
- `SECURITY.md`：安全漏洞反馈流程

## 许可证

GPL-2.0-only
