# 贡献指南

感谢参与改进 Kernel-Xiaomi-Umi。

## 适用范围

迁移编排仓库（工作流 + 脚本 + 诊断），不是内核源码。

## 开始前

1. 阅读 `README-Zh-Cn.md`
2. 阅读 `Porting-Plan.md`
3. 查看 `Porting/CHANGELOG.md`

## 分支策略

- `port/phase*` — 阶段性开发
- `port/hotfix-*` — 紧急修复

## PR 要求

- 变更内容与动机
- 验证证据
- 风险说明

## 来源规则

参考源统一维护在 `README-Zh-Cn.md` 和 `Porting/README.md`。

- 作者 ID 仅用于发现
- 禁止整树盲拷贝
- 禁止导入 proprietary blob

## 质量

- 行为变化时更新文档
- 要求 CI 证据
- 保持 `CHANGELOG.md` 简洁
- 遵循 `README-Zh-Cn.md` 中的仓库清洁约定

## 安全

- 禁止提交密钥
- 保持 `.gitignore` 干净
