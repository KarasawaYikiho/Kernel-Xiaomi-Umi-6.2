# Porting Changelog

> Milestone-only changelog.

## 2026-03-26

- Tightened the postprocess chain so local reruns now rebuild driver integration evidence, re-sync the manifest, and validate AnyKernel/boot image inputs before regenerating the consolidated phase2 report.
- Preserved existing `artifacts/runtime-validation-input.md` content during postprocess reruns to avoid wiping manual device-side validation results.
- Prefer the local official UMI ROM package as the first release `boot.img` fallback and expose ROM boot size/hash alignment in `bootimg-info.txt`.
- Raised artifact readiness from a DTB-only heuristic to a ROM-aware gate that also records release readiness, AnyKernel validity, DTB manifest hits, and official boot image alignment across reports, badges, and metrics.
- Hardened shell entrypoints to auto-detect `python3` or `python`, so local Windows reruns of postprocess/build helpers no longer fail just because `python3` is absent.
- Added local postprocess fallback metadata and downgraded artifact completeness to `partial` when Phase2-only build artifacts are absent, preventing misleading DTB-focused next-step recommendations on ROM-only validation runs.
- Made DTB manifest collection and artifact packaging more resilient for weak/local environments by keeping empty DTB outputs explicit, enriching AnyKernel reasons, and skipping zip packaging gracefully when the host lacks `zip`.
- Improved AnyKernel candidate diagnostics to reuse existing templates, fall back to `artifacts/Image.gz`, and surface the exact packaging blocker in reports, badges, and metrics.
- Added `target_dtb_manifest_debug.txt` so DTB candidate inference is traceable from source path to generated alias, and surfaced DTB debug artifacts in summary/index outputs.
- Tightened driver-integration progress so ROM boot/dtbo/vbmeta consistency stays pending until actually verified, and shifted runtime guidance toward Magisk patching when the ROM-aligned `artifacts/boot.img` is already ready.
- Extract official ROM `dtbo.img` and `vbmeta.img` into `artifacts/` alongside the ROM-aligned `boot.img`, so postprocess can close ROM consistency follow-ups with local evidence instead of leaving them perpetually pending.
- Recentered runtime guidance on the Magisk-patched `artifacts/boot.img` path so AnyKernel packaging no longer dominates device validation messaging once the ROM-aligned boot image is ready.
- Tightened the runtime feedback loop by recording the Magisk-patched boot filename/method in `runtime-validation-input.md` and marking untouched device-check templates as `awaiting_device_validation` instead of a generic success state.
- Propagated `awaiting_device_validation`, Magisk readiness, and patched-boot metadata into badges and metrics so every top-level status view reflects the same device-test state.
- Tightened driver-integration evidence to distinguish real target-tree driver presence from inventory/reference hints, and now keep `target_tree_missing_for_driver_validation` explicit when local driver integration cannot actually be verified.
- Reduced script duplication by centralizing shell Python detection in `Tools/Porting/Common.sh`, reusing CSV parsing from `Tools/Porting/Kv_Utils.py`, and sharing driver-manifest parsing through `Tools/Porting/Manifest.py`.

## 2026-03-11

- Refactored postprocess scripts to share a centralized KV parser (`Tools/Porting/Kv_Utils.py`), removing duplicated parsing logic.
- Kept decision/report chain behavior intact while reducing maintenance overhead.
- Performed repo-wide documentation rewrite for consistency and readability.

## 2026-03-09

- Added AnyKernel candidate zip packaging in Phase2 workflow (`AnyKernel3-umi-candidate.zip`).
- Expanded migration statistics and diagnostics/reporting chain.
- Improved workflow reliability with concurrency control and timeout handling.
- Simplified compile flow by removing obsolete quality-gate path.

## 2026-03-08

- Initialized 5+ porting orchestrator skeleton.
- Added capability inventory and first classification/gap outputs.
- Started automated Phase2 migration/build attempts for `umi`.
