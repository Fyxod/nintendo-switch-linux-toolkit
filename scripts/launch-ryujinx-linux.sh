#!/usr/bin/env bash
set -euo pipefail

: "${RYUJINX_BIN:?Set RYUJINX_BIN to the emulator executable}"
: "${RYUJINX_DATA_DIR:?Set RYUJINX_DATA_DIR to the emulator user-data directory}"
: "${SWITCH_GAME_FILE:?Set SWITCH_GAME_FILE to a legally obtained game dump}"

if [[ ! -x "$RYUJINX_BIN" ]]; then
  printf 'Emulator is not executable: %s\n' "$RYUJINX_BIN" >&2
  exit 1
fi
if [[ ! -f "$SWITCH_GAME_FILE" ]]; then
  printf 'Game file is missing: %s\n' "$SWITCH_GAME_FILE" >&2
  exit 1
fi

launcher_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
log_path="${RYUJINX_LOG_PATH:-${XDG_STATE_HOME:-$HOME/.local/state}/nintendo-switch-linux-toolkit/last-launch.log}"
mkdir -p -- "$(dirname -- "$log_path")" "$RYUJINX_DATA_DIR"

if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then
  export __NV_PRIME_RENDER_OFFLOAD=1
  export __VK_LAYER_NV_optimus=NVIDIA_only
  export __GLX_VENDOR_LIBRARY_NAME=nvidia
fi

export DOTNET_EnableAlternateStackCheck=1
command_line=()

if command -v powerprofilesctl >/dev/null 2>&1 && powerprofilesctl list 2>/dev/null | grep -q 'performance:'; then
  command_line+=(powerprofilesctl launch --profile performance
    --reason 'Nintendo Switch emulator' --appid nintendo-switch-linux-toolkit)
fi

if [[ "${USE_NATIVE_DISPLAY_SESSION:-1}" == 1 ]] && [[ "${XDG_SESSION_TYPE:-x11}" == x11 ]]; then
  command_line+=(python3 "$launcher_dir/display-session.py"
    --mode "${GAME_DISPLAY_MODE:-1920x1080}"
    --rate "${GAME_DISPLAY_RATE:-60}" --)
fi

if command -v gamemoderun >/dev/null 2>&1; then
  command_line+=(gamemoderun)
fi

command_line+=("$RYUJINX_BIN" --root-data-dir "$RYUJINX_DATA_DIR")
if [[ "${RYUJINX_HANDHELD_MODE:-1}" == 1 ]]; then
  command_line+=(--handheld-mode)
fi
command_line+=("$SWITCH_GAME_FILE")

exec "${command_line[@]}" >"$log_path" 2>&1
