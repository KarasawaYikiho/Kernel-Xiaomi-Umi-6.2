# Agent Instructions

## Branch Policy

- `main` is the lightweight orchestration branch. It must not contain the imported Linux kernel source tree.
- `master` is the full kernel-source branch. It contains the yefxx-based Linux kernel source, Umi device targets, Porting tools, and GitHub Actions that build the kernel.
- GitHub Actions for kernel builds and ROM-aligned kernel packaging must run from `master`.
- Daily planning, branch-policy documentation, and lightweight repository metadata may be maintained on `main`.
- Finished kernel-source work must be committed and pushed to `master`.
- Local development may use a local kernel source checkout, but remote kernel-source publication belongs on `master`.

## Source Roles

- yefxx `xiaomi-umi-linux-kernel` is the kernel source baseline.
- SO-TS 4.19 is reference-only for workflow patterns and targeted comparison.
- Official Xiaomi ROM artifacts are validation-only evidence, not source-code donors.

## Naming Policy

- Project-owned documentation and tooling names should use independent-word TitleCase when safe.
- Do not rename imported Linux kernel source paths to TitleCase. Kernel source paths follow upstream lowercase/Kbuild conventions.
- When renaming any project-owned file, update all code, workflow, and documentation references in the same change.

## Verification Policy

- Before reporting completion, run the Python Porting selftests and repository sanity check.
- For kernel-source branch changes, also run WSL/Linux Kbuild checks for `umi_defconfig` and `qcom/sm8250-xiaomi-umi.dtb` when the toolchain is available.
