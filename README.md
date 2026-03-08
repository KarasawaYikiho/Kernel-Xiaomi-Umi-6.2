# Xiaomi 10 (umi) 高版本内核构建（GitHub Actions）

本项目用于在 **GitHub Actions** 上构建小米 10（umi）可用的高版本内核（`>5`）。

## 数据来源（全部来自 GitHub）

1. 内核源码：`yefxx/xiaomi-umi-linux-kernel`
   - https://github.com/yefxx/xiaomi-umi-linux-kernel
   - `Makefile` 显示版本主号：`VERSION = 6`（满足 >5）
2. CI 平台：GitHub Actions
   - https://github.com/features/actions

## 设计说明

- 在云端（Actions）构建，避免本地环境额外下载/配置设备树、工具链等。
- Workflow 会自动：
  - 拉取内核仓库
  - 安装编译依赖
  - 严格检测 `umi_defconfig`（不存在则直接失败，避免编出“假 umi 包”）
  - 编译 `Image.gz` / `dtbs` / `modules`
  - 产出两类 artifacts：
    - `umi-kernel-slim-*`（内核镜像 + 关键 dtb）
    - `umi-kernel-full-*`（`modules` + `out` 压缩包，体积通常显著更大）

## 使用方法

1. 在 GitHub 创建新仓库并推送本目录内容。
2. 进入仓库 Actions 页面，手动触发 `Build Xiaomi 10 (umi) Kernel > 5`。
3. 触发时填写：
   - `kernel_repo`：你要编译的 GitHub 内核仓库（必须含 `umi_defconfig`，且 `VERSION > 5`）
   - `kernel_branch`：对应分支
4. 构建完成后，在 Artifacts 下载 `umi-kernel-*`。

## 注意

- 不同 ROM/引导链对内核与模块、dtb/dtbo 的匹配要求不同。
- 本流程重点是“可复现地构建 >5 内核”，刷机前请确认与你的 ROM/boot/vendor 兼容。
