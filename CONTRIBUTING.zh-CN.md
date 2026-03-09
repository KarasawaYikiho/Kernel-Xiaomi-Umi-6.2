# 贡献指南

感谢你参与改进 **Kernel-Xiaomi-Umi**。

## 适用范围

本仓库是**内核迁移编排仓库**（CI 工作流 + 迁移/诊断工具），不是完整内核源码仓。

## 开始前请先阅读

1. `README.zh-CN.md`（或 `README.md`）
2. `porting/README.md`
3. `PORTING_PLAN.md` 与最新的 `porting/CHANGELOG.md`

## 分支规范

请遵循 `porting/BRANCHING.md`：

- `port/phase*`：阶段性开发
- `port/hotfix-*`：紧急修复

## Pull Request 要求

请使用 PR 模板，并至少包含：

- 变更摘要与影响范围
- 验证说明（运行记录/工件）
- 风险评估与回滚方案（涉及 workflow/script 时必须提供）

## 变更期望

- 输出或行为发生变化时，必须同步更新文档。
- 优先保证 CI 结果可复现，避免只在本地可运行的改动。
- 新增诊断工具请放在 `tools/porting/`，并更新 `tools/porting/README.md`。

## Changelog 规范

- 里程碑级更新写入 `porting/CHANGELOG.md`（保持简洁）。
- 详细历史可放入归档文件（archive）。

## 安全与合规

- 禁止提交密钥、令牌或任何敏感凭据。
- 保持 `.gitignore` 干净，避免提交本地噪声文件。
- 生成型工件默认视为临时产物，除非明确要求入库。
