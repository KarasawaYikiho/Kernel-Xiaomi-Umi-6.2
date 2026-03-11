#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Check_Target_Kernel_Version.sh

grep -E '^(VERSION|PATCHLEVEL|SUBLEVEL)\s*=\s*' target/Makefile
