#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Apply_Phase2_Migration.sh <device>

DEVICE="${1:-${DEVICE:-umi}}"

chmod +x Tools/Porting/Phase2Apply.sh
  ./Tools/Porting/Phase2Apply.sh "$PWD/source" "$PWD/target" "$DEVICE"
