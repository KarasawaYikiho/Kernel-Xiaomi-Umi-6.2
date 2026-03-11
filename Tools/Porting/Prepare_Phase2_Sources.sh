#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Prepare_Phase2_Sources.sh <source_repo> <source_branch> <target_repo> <target_branch>

SOURCE_REPO="${1:?source_repo required}"
SOURCE_BRANCH="${2:?source_branch required}"
TARGET_REPO="${3:?target_repo required}"
TARGET_BRANCH="${4:?target_branch required}"

rm -rf source target

git clone --depth=1 --branch "$SOURCE_BRANCH" "$SOURCE_REPO" source
git clone --depth=1 --branch "$TARGET_BRANCH" "$TARGET_REPO" target
