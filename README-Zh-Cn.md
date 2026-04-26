# Kernel-Xiaomi-SM8250

[English](README.md) | 简体中文

基于 `yefxx/xiaomi-umi-linux-kernel` 的 Xiaomi SM8250 系列设备内核源码树，当前以 `umi` 作为 ROM 对齐参考设备。

本仓库现在是内核源码树。SO-TS 4.19 仅作为定向对比参考，官方 Xiaomi ROM 仅作为 boot-chain 与打包对齐的验证证据。

## 分支策略

- `main`：轻量编排分支，不包含导入的 Linux 内核源码。
- `master`：完整 yefxx-based 内核源码分支；内核 GitHub Actions 从这里运行。
- 持久化的 agent/项目规则见 `AGENTS.md`。

## 职责

- Linux 内核源码、DTS、defconfig、驱动、CI、脚本与文档
- GitHub Actions Phase2 迁移与 ROM 对齐自动化
- 结构化诊断、指标与可直接刷入的产物交付

## 快速开始

运行 **`Build-Umi-Kernel.yml`** 构建当前检出的内核源码树，或运行 **`ROM-Aligned-Umi-Port.yml`** 生成 ROM 对齐证据与打包产物。优先检查：

| 产物 | 作用 |
|-----|------|
| `artifacts/plan-progress.md` | 将 `PortingPlan.md` 与当前产物证据对齐，展示阶段进度与 Phase 2 清单完成度 |
| `artifacts/phase2-report.txt` | 汇总迁移阶段状态与阻塞项 |
| `artifacts/next-focus.txt` | 给出下一步优先处理事项 |
| `artifacts/runtime-validation-summary.md` | 汇总运行验证结果 |
| `artifacts/anykernel-info.txt` | 记录 AnyKernel 打包状态 |

## 输入

| 输入 | 默认值 | 描述 |
|-----|--------|-------------|
| `device` | `umi` | 设备代号；当前默认参考基线仍为 `umi` |

参考源、路径、默认分支和 boot 大小来源不再作为工作流输入手动填写，而是由代码自动填充：

- yefxx 基线元数据、SO-TS 参考源元数据、工具链下载源、参考 ROM 本地路径统一收敛到 `Porting/Sm8250PortConfig.json`
- 维护者本地 ROM 目录：`D:\GIT\MIUI_UMI`
- 维护者本地 ROM zip 回退：`D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip`
- GitHub Action 回退：仓库跟踪的 `Porting/OfficialRomBaseline/BootImgParts/` 分片会在 CI 中自动重组
- `BOOTIMG_REQUIRED_BYTES`：优先从当前 ROM 基线自动推导，只有在基线元数据缺失时才退回默认值

## 工作流

- **`ROM-Aligned-Umi-Port.yml`** — `master` 上当前 `umi` 参考 ROM 基线下的 SM8250 ROM 对齐迁移流程
- **`Build-Umi-Kernel.yml`** — `master` 上 SM8250 家族设备的云端构建流程

## 本地 Boot 基线

在这台机器上，最短 Windows 入口是：

直接使用 `Porting/Tools/RunLocalOfficialRomBaseline.ps1`；具体刷新产物和本地校验步骤统一收敛到 `Porting/Tools/README.md`，避免多处重复维护。

它默认使用 `D:\GIT\MIUI_UMI`，无需把官方 `boot.img` 提交进 Git。

## 仓库清洁约定

- `artifacts/`、`out/`、`source/`、`target/` 是工作流和本地验证生成的工作目录
- `source.extract/`、`target.extract/` 与 `source.zip` 是本地抓取/解包产物，也应保持未跟踪
- `.ruff_cache/` 与 `__pycache__/` 是本地工具缓存
- 这些路径应保持未跟踪状态，避免污染提交记录
- `Porting/OfficialRomBaseline/` 用于存放可检入的 ROM 基线元数据和小体积校验镜像，供校验流程使用
- 执行基线见 `PortingPlan.md`，文档阅读顺序见 `Porting/README.md`，本地校验入口见 `Porting/Tools/README.md`

## 参考源

- 源码基线: `yefxx/xiaomi-umi-linux-kernel`（`master`，Linux 6.11 快照）
- 仅参考 SO-TS: `android_kernel_xiaomi_sm8250` (4.19)
- 驱动参考: `UtsavBalar1231/*`
- 通用配置源: `Porting/Sm8250PortConfig.json`

## 许可证

GPL-2.0-only
