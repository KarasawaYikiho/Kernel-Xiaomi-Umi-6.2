# Kernel-Xiaomi-Umi

[English README](./README.md)

Kernel-Xiaomi-Umi 是一个面向 Xiaomi 10（umi）内核迁移任务的**编排仓库**，用于自动化执行 Phase2 迁移、构建尝试、诊断汇总与工件打包。

> 本仓库**不是**完整内核源码仓。

## 仓库功能

- 通过 GitHub Actions 执行内核构建/迁移流程
- 执行 SO-TS 4.19 → 5+ 基线的 Phase2 迁移
- 生成结构化诊断与决策工件
- 产出候选打包结果（含 AnyKernel 候选包）

## 仓库最终目标

- 产出 **Release 级、可直接刷入的 `boot.img`**（面向 umi）
- 保证 **同机型可复现**：相同机型 + 相同 workflow 输入，可在 GitHub Actions 稳定自助编译并产出可刷写工件
- 在保留 Phase2 诊断工件能力的前提下，将交付目标从“候选包”推进到“release `boot.img` + 验证清单”

## 上游参考

- SO-TS 参考源：`SO-TS/android_kernel_xiaomi_sm8250`
- URL：<https://github.com/SO-TS/android_kernel_xiaomi_sm8250>

## 工作流

### 快速开始（推荐）

先以默认参数运行 **`phase2-port-umi.yml`**，随后按顺序查看：

1. `artifacts/phase2-report.txt`
2. `artifacts/build-exit.txt`
3. `artifacts/build-error-summary.txt`
4. `artifacts/anykernel-info.txt`
5. `artifacts/next-focus.txt`

该顺序可快速判断本轮是否通过，以及下一步应优化方向。

### `build-umi-kernel.yml`

参考式云端构建流程：

1. 安装依赖并配置 ccache
2. 下载 ZyC Clang 15
3. 克隆目标内核仓库/分支
4. 按设备参数运行 `build.sh`（可选 KernelSU）
5. 上传构建产物

输入参数：

- `kernel_repo`
- `kernel_branch`
- `device`（默认 `umi`）
- `ksu`（默认 `false`）

### `phase2-port-umi.yml`

Phase2 迁移 + 构建 + 诊断流程：

1. 准备 source/target 源码树
2. 执行 Phase2 迁移
3. 执行核心构建与 DTB 目标构建
4. 收集工件并生成 umi 聚焦包
5. 构建 AnyKernel 候选包
6. 生成汇总报告并上传全部工件

输入参数：

- `source_repo`
- `source_branch`
- `target_repo`
- `target_branch`
- `device`（默认 `umi`）
- `bootimg_required_bytes`（默认 `268435456`，即 256MiB）
- `bootimg_ramdisk_url`（可选：用于下载 `ramdisk.cpio.gz`，也支持填写包含 ramdisk 的 zip 链接）
- `bootimg_prebuilt_url`（可选：当缺少 ramdisk 时，下载预构建 `boot.img`，也支持填写包含 `boot.img` 的 zip 链接）

快速使用建议：

- 能提供匹配机型/基线的 `ramdisk.cpio.gz` 时，优先使用 `bootimg_ramdisk_url`。
- 无法在 CI 提供 ramdisk 时，使用 `bootimg_prebuilt_url` 作为回退。
- 两者同时提供时，当前流程会先尝试 prebuilt 回退，再走 mkbootimg 构建路径。
- 两个 URL 入参均支持“直链文件”或“zip 链接”（best-effort 自动提取 `ramdisk*.cpio.gz` / `boot.img`）。
- `mkbootimg` 现已做 best-effort 自动解析（系统/用户路径、仓内脚本、python 模块，最后回退到远程拉取 `mkbootimg.py`）。

## 关键脚本

核心编排脚本：

- `tools/porting/install_ci_deps.sh`
- `tools/porting/prepare_phase2_sources.sh`
- `tools/porting/check_target_kernel_version.sh`
- `tools/porting/apply_phase2_migration.sh`
- `tools/porting/run_phase2_build.sh`
- `tools/porting/collect_phase2_artifacts.sh`
- `tools/porting/build_anykernel_candidate.sh`
- `tools/porting/write_run_meta.sh`
- `tools/porting/run_postprocess_suite.sh`

完整脚本索引：

- `tools/porting/README.md`

## Phase2 工件速读

建议优先查看：

- `artifacts/phase2-report.txt`：单文件汇总
- `artifacts/build-exit.txt`：`defconfig_rc` / `build_rc` / `dtbs_rc`
- `artifacts/build-error-summary.txt`：关键报错摘要
- `artifacts/anykernel-info.txt`：AnyKernel 候选包状态
- `artifacts/next-focus.txt`：下一轮优化建议

补充诊断工件：

- `artifacts/make-defconfig.log`
- `artifacts/make-build.log`
- `artifacts/make-target-dtbs.log`
- `artifacts/make-dtb-manifest.log`
- `artifacts/dtb-postcheck.txt`
- `artifacts/dtb-miss-analysis.txt`
- `artifacts/phase2-metrics.json`

## 仓库结构

- `.github/workflows/`：CI 工作流
- `tools/porting/`：迁移与诊断工具
- `porting/`：计划、盘点、报告、变更记录

## 文档入口

- 移植文档索引：`porting/README.md`
- 脚本索引：`tools/porting/README.md`
- 英文文档：`README.md`

## 贡献

- 中文贡献指南：`CONTRIBUTING.zh-CN.md`
- 英文贡献指南：`CONTRIBUTING.md`
- 代码所有者：`.github/CODEOWNERS`

## 许可证

本项目采用 **GPL-2.0-only**（GNU General Public License v2.0 only）许可证，详见 `LICENSE`。
