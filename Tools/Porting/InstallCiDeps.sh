#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y \
  git bc bison flex libssl-dev make libc6-dev libncurses5-dev \
  crossbuild-essential-arm64 ccache pahole lz4 xz-utils zstd \
  python3 clang lld llvm zip
