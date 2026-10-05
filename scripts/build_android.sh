#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
export cores=${PPPLAYER_BUILD_JOBS:-2}
cd "$ROOT/buildscripts"
case "${1:-x86_64}" in
  x86_64|arm64) ./build.sh --arch "${1:-x86_64}" ;;
  *) echo 'Supported targets: x86_64, arm64' >&2; exit 2 ;;
esac
