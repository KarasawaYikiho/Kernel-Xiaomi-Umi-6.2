#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Apply_Phase2_Migration.sh <device>

DEVICE="${1:-${DEVICE:-umi}}"

source "Porting/Tools/Common.sh"
initialize_porting_paths

chmod +x Porting/Tools/Phase2Apply.sh
./Porting/Tools/Phase2Apply.sh "$REFERENCE_DIR" "$KERNEL_DIR" "$DEVICE"
