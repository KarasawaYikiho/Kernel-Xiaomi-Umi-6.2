# Kernel-Xiaomi-SM8250

[English](README.md) | 简体中文

面向 Xiaomi SM8250 系列设备的内核迁移编排仓库。CI 驱动从 SO-TS 4.19 迁移到 5+ 基线，当前默认参考 ROM 基线仍为 `umi`，但工作流配置已统一为 SM8250 家族通用配置层。

> 本仓库**不是**内核源码树。

## 职责

- GitHub Actions Phase2 迁移自动化
- 结构化诊断与指标
- 可直接刷入的产物交付

## 快速开始

运行 **`ROM-Aligned-Umi-Port.yml`** 工作流（当前 `umi` 参考基线的 SM8250 通用流程）后，优先检查下列产物：

| 产物 | 作用 |
|-----|------|
| `artifacts/plan-progress.md` | 将 `Porting-Plan.md` 与当前产物证据对齐，展示阶段进度与 Phase 2 清单完成度 |
| `artifacts/phase2-report.txt` | 汇总迁移阶段状态与阻塞项 |
| `artifacts/next-focus.txt` | 给出下一步优先处理事项 |
| `artifacts/runtime-validation-summary.md` | 汇总运行验证结果 |
| `artifacts/anykernel-info.txt` | 记录 AnyKernel 打包状态 |

## 输入

| 输入 | 默认值 | 描述 |
|-----|--------|-------------|
| `device` | `umi` | 设备代号；当前默认参考基线仍为 `umi` |

链接、路径、默认分支和 boot 大小来源不再作为工作流输入手动填写，而是由代码自动填充：

- 源仓库、目标仓库、默认分支、工具链下载源、参考 ROM 本地路径统一收敛到 `Porting/Sm8250PortConfig.json`
- 维护者本地 ROM 目录：`D:\GIT\MIUI_UMI`
- 维护者本地 ROM zip 回退：`D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip`
- GitHub Action 回退：仓库跟踪的 `Porting/OfficialRomBaseline/BootImgParts/` 分片会在 CI 中自动重组
- `BOOTIMG_REQUIRED_BYTES`：优先从当前 ROM 基线自动推导，只有在基线元数据缺失时才退回默认值

## 工作流

- **`ROM-Aligned-Umi-Port.yml`** — 当前 `umi` 参考 ROM 基线下的 SM8250 主 ROM 对齐迁移流程
- **`Build-Umi-Kernel.yml`** — SM8250 家族设备的云端构建参考流程

## 本地 Boot 基线

在这台机器上，最短 Windows 入口是：

直接使用 `Tools/Porting/RunLocalOfficialRomBaseline.ps1`；具体刷新产物和本地校验步骤统一收敛到 `Tools/Porting/README.md`，避免多处重复维护。

它默认使用 `D:\GIT\MIUI_UMI`，无需把官方 `boot.img` 提交进 Git。

## 仓库清洁约定

- `artifacts/`、`source/`、`target/` 是工作流和本地验证生成的工作目录
- `source.extract/`、`target.extract/` 与 `source.zip` 是本地抓取/解包产物，也应保持未跟踪
- `.ruff_cache/` 与 `__pycache__/` 是本地工具缓存
- 这些路径应保持未跟踪状态，避免污染提交记录
- `Porting/OfficialRomBaseline/` 用于存放可检入的 ROM 基线元数据和小体积校验镜像，供校验流程使用
- 执行基线见 `Porting-Plan.md`，文档阅读顺序见 `Porting/README.md`，本地校验入口见 `Tools/Porting/README.md`

## 参考源

- SO-TS: `android_kernel_xiaomi_sm8250` (4.19)
- 5+ 基线: `yefxx/xiaomi-umi-linux-kernel`
- 驱动参考: `UtsavBalar1231/*`
- 通用配置源: `Porting/Sm8250PortConfig.json`

## 许可证

GPL-2.0-only
