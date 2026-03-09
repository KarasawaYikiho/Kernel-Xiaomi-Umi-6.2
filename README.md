# Kernel-Xiaomi-Umi

Xiaomi 10 (umi) kernel build/porting orchestrator.

This repository provides GitHub Actions workflows and helper scripts to:
- build kernel artifacts in CI
- run Phase2 porting steps from SO-TS 4.19 to a 5+ baseline
- generate diagnostics and packaging candidates (including AnyKernel candidate zip)

## Reference

- Source reference: `SO-TS/android_kernel_xiaomi_sm8250`
- URL: https://github.com/SO-TS/android_kernel_xiaomi_sm8250

## Workflows

### 1) build-umi-kernel.yml
Reference-style cloud build flow:
1. install dependencies + setup ccache
2. download ZyC Clang 15
3. clone target kernel repo/branch
4. run `build.sh` with selected `device` and optional `ksu`
5. upload build artifacts

Inputs:
- `kernel_repo`
- `kernel_branch`
- `device` (default: `umi`)
- `ksu` (default: `false`)

### 2) phase2-port-umi.yml
Phase2 migration + build attempt flow:
1. clone source (4.19) and target (5+) trees
2. apply `tools/porting/phase2_apply.sh`
3. attempt target kernel build
4. collect dtb diagnostics and umi-focused bundle
5. generate AnyKernel candidate package
6. generate consolidated report and upload artifacts

Inputs:
- `source_repo`
- `source_branch`
- `target_repo`
- `target_branch`
- `device` (default: `umi`)

## Key Scripts

- `tools/porting/phase2_apply.sh` — defconfig + include-aware dts/dtsi migration
- `tools/porting/build_dtb_manifest.py` — derive target dtb manifest from migrated dts list
- `tools/porting/dtb_postcheck.py` — hit/miss + hit_ratio stats for manifest mapping
- `tools/porting/analyze_dtb_miss.py` — bucketized miss analysis
- `tools/porting/evaluate_artifact.py` — flash-readiness heuristic
- `tools/porting/build_phase2_report.py` — consolidated phase2 summary
- `tools/porting/README.md` — full script index and execution order
- `tools/porting/run_postprocess_suite.sh` — one-shot postprocess orchestrator

## Artifact Quick Read (Phase2)

After each `phase2-port-umi.yml` run, check in order:
- `artifacts/phase2-report.txt` (single-file summary)
- `artifacts/run-meta.txt` (run inputs + revision metadata)
- `artifacts/artifact-completeness.txt` (required/optional artifact completeness)
- `artifacts/build-exit.txt` (`defconfig_rc` / `build_rc`)
- `artifacts/make-defconfig.log` / `artifacts/make-build.log`
- `artifacts/flash-readiness.txt`
- `artifacts/dtb-postcheck.txt`
- `artifacts/dtb-miss-analysis.txt`
- `artifacts/anykernel-info.txt`
- `artifacts/next-focus.txt` (recommended next optimization direction)
- `artifacts/build-error-summary.txt` (condensed error clues from make logs)
- `artifacts/artifact-index.txt` (artifact list with file sizes)
- `artifacts/artifact-summary.md` (human-friendly markdown summary)
- `artifacts/phase2-report-validate.txt` (schema/key presence check)
- `artifacts/phase2-metrics.json` (structured metrics for automation/dashboard)
- `artifacts/status-badge-line.txt` (one-line status snapshot)
- `artifacts/artifact-sha256.txt` (sha256 checksums for uploaded artifacts)

## Repository Layout

- `.github/workflows/` — CI workflows
- `tools/porting/` — migration/analysis tooling
- `porting/` — plans, inventory, reports, changelog

## Documentation Entry

- Porting docs index: `porting/README.md`
- Tooling script index: `tools/porting/README.md`

## License

See `LICENSE`.
