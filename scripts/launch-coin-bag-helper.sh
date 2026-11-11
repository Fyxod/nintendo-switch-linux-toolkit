#!/usr/bin/env bash
set -euo pipefail

: "${BROWSER_BIN:?Set BROWSER_BIN to Brave, Chrome, or Edge}"
helper_url="${COIN_BAG_HELPER_URL:-https://na-ji.github.io/pokemon-go-coin-bag/}"
profile_dir="${COIN_BAG_PROFILE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/pokemon-go-coin-bag/browser}"
mkdir -p -- "$profile_dir"
chmod 700 "$profile_dir"

flags=(
  --user-data-dir="$profile_dir"
  --no-first-run
  --no-default-browser-check
  --app="$helper_url"
)
case "$(basename -- "$BROWSER_BIN")" in
  *brave*) flags+=(--enable-features=BraveWebBluetoothAPI --enable-experimental-web-platform-features) ;;
esac

exec "$BROWSER_BIN" "${flags[@]}"
