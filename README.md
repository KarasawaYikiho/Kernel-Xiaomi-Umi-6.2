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
  - 自动检测 `umi_defconfig`（若存在优先使用）
  - 编译 `Image.gz` / `dtbs` / `modules`
  - 上传构建产物

## 使用方法

1. 在 GitHub 创建新仓库并推送本目录内容。
2. 进入仓库 Actions 页面，手动触发 `Build Xiaomi 10 (umi) Kernel > 5`。
3. 构建完成后，在 Artifacts 下载 `umi-kernel-*`。

## 注意

- 不同 ROM/引导链对内核与模块、dtb/dtbo 的匹配要求不同。
- 本流程重点是“可复现地构建 >5 内核”，刷机前请确认与你的 ROM/boot/vendor 兼容。
