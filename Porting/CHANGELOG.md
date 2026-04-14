# Changelog

> Milestone-only changelog.

## 2026-04-14

- Fixed workflow script name errors causing exit code 127
- Fixed internal script references (Phase2Apply, etc.)
- Fixed Python comment references (FetchInventory, SyncDriverIntegrationManifest)
- Rewrote all README files for consistency

## 2026-03-26

- Tightened postprocess chain with driver integration evidence
- Preserved runtime-validation-input.md during reruns
- ROM-aware artifact readiness gate
- Added python/python3 auto-detection for Windows compatibility
- Reduced script duplication via Common.sh and KvUtils.py

## 2026-03-11

- Refactored postprocess with centralized KV parser
- Documentation rewrite for consistency

## Legacy

See git history for earlier milestones.