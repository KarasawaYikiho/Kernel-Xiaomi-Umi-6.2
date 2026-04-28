# 贡献指南

感谢参与改进 Kernel-Xiaomi-Umi。

## 适用范围

内核源码、DTS、defconfig、驱动、GitHub workflows、迁移脚本、诊断与文档。

## 开始前

1. 阅读 `ReadmeZhCn.md`
2. 阅读 `PortingPlan.md`
3. 查看 `Porting/CHANGELOG.md`

## 分支策略

- `port/phase*` — 阶段性开发
- `port/hotfix-*` — 紧急修复

## PR 要求

- 变更内容与动机
- 验证证据
- 内核、DTS、defconfig、工作流和脚本变更的风险说明

## 来源规则

源码与参考源角色统一维护在 `ReadmeZhCn.md` 和 `Porting/README.md`。

- yefxx 是源码基线
- SO-TS 仅用于定向对比参考
- 官方 ROM 产物仅用于验证，不能作为代码 donor
- 禁止整树盲拷贝
- 禁止导入 proprietary blob

## 质量

- 行为变化时更新文档
- 要求 CI 证据
- 保持 `CHANGELOG.md` 简洁
- 遵循 `ReadmeZhCn.md` 中的仓库清洁约定

## 安全

- 禁止提交密钥
- 保持 `.gitignore` 干净
