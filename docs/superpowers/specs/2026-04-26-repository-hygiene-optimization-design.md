# Repository Hygiene Optimization Design

## Goal

Optimize both long-lived branches while preserving their roles: `main` remains a source-free orchestration branch, and `master` remains the full kernel-source branch. The optimization removes machine-local paths from tracked content, tightens automated hygiene checks, reduces duplicated maintainer-path documentation, and keeps kernel-source naming untouched.

## Scope

- Project-owned files may be edited: root docs, `Porting/`, `.github/`, and `docs/superpowers/`.
- Imported Linux kernel source paths must not be renamed or TitleCased.
- File-content checks apply to tracked files on both branches.
- Local-only Git metadata and ignored `.learnings/` files are outside the repository content contract.

## Approach

Use a narrow, verification-backed cleanup. Replace hard-coded local ROM paths with environment-variable based examples, make `Porting/Sm8250PortConfig.json` defaults portable, and add a repository sanity check that rejects tracked machine-local paths. Keep existing script names unless workflows and tests already reference the new names.

## Testing

- First prove the new local-path sanity test fails against the current tracked content.
- Update config/docs and sanity code.
- Re-run the sanity test and Porting selftests.
- Verify `main` still lacks kernel source roots and `master` still contains them.

## Branch Execution

Apply and push the same project-owned cleanup to `master`, then apply and push the compatible source-free cleanup to `main`. `master` keeps kernel build validation; `main` uses non-kernel sanity validation.
