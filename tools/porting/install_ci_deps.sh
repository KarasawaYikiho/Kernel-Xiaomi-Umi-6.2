#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y \
  git bc bison flex libssl-dev make libc6-dev libncurses5-dev \
  crossbuild-essential-arm64 ccache pahole lz4 xz-utils zstd \
  python3 python3-pip clang lld llvm zip

# Best-effort boot image tooling (used by prepare_release_bootimg.sh)
python3 -m pip install --user --upgrade pip || true
python3 -m pip install --user mkbootimg || true
# Ensure user-level scripts are discoverable in CI shells.
if [[ -x "$HOME/.local/bin/mkbootimg" ]]; then
  sudo ln -sf "$HOME/.local/bin/mkbootimg" /usr/local/bin/mkbootimg || true
fi
if [[ -x "$HOME/.local/bin/mkbootimg.py" ]]; then
  sudo ln -sf "$HOME/.local/bin/mkbootimg.py" /usr/local/bin/mkbootimg.py || true
fi
