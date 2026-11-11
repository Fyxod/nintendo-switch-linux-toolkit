#!/usr/bin/env bash
set -euo pipefail

config_path="${1:-}"

section() { printf '\n[%s]\n' "$1"; }
run_if_present() {
  local command_name="$1"
  shift
  if command -v "$command_name" >/dev/null 2>&1; then "$@"; else printf '%s unavailable\n' "$command_name"; fi
}

section system
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  printf 'OS: %s\n' "${PRETTY_NAME:-unknown}"
fi
printf 'Kernel: %s\n' "$(uname -srmo)"
printf 'Session: %s\n' "${XDG_SESSION_TYPE:-unknown}"
lscpu | awk -F: '/Model name|Socket|Core\(s\)|Thread\(s\)/ {gsub(/^[ \t]+/,"",$2); print $1 ": " $2}'
free -h

section power
run_if_present powerprofilesctl powerprofilesctl get
for supply in /sys/class/power_supply/AC*/online; do
  [[ -r "$supply" ]] && printf 'AC online: %s\n' "$(cat "$supply")"
done

section graphics
run_if_present nvidia-smi nvidia-smi \
  --query-gpu=name,driver_version,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,clocks.gr,pstate \
  --format=csv
if command -v vulkaninfo >/dev/null 2>&1; then
  vulkaninfo --summary 2>/dev/null | sed -n '1,80p'
fi

section thermal
run_if_present sensors sensors

section display
if [[ "${XDG_SESSION_TYPE:-x11}" == x11 ]] && command -v xrandr >/dev/null 2>&1; then
  xrandr --query | sed -n '1,35p'
else
  printf 'X11 display diagnostics unavailable for this session.\n'
fi

section load
uptime
ps -eo pid,comm,%cpu,%mem,rss,stat --sort=-%cpu | head -n 16
ps -C Ryujinx -o pid,comm,%cpu,%mem,rss,stat 2>/dev/null || true

if [[ -n "$config_path" ]]; then
  section emulator_config
  python3 - "$config_path" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text())
allowed = (
    'version', 'backend_threading', 'res_scale', 'res_scale_custom',
    'max_anisotropy', 'anti_aliasing', 'scaling_filter', 'docked_mode',
    'enable_vsync', 'vsync_mode', 'enable_shader_cache',
    'enable_texture_recompression', 'enable_macro_hle', 'enable_ptc',
    'enable_low_power_ptc', 'tick_scalar', 'memory_manager_mode',
    'graphics_backend', 'preferred_gpu', 'use_hypervisor',
)
for key in allowed:
    if key in data:
        value = data[key]
        if key == 'preferred_gpu' and value:
            value = '<configured>'
        print(f'{key}: {value!r}')
PY
fi

section privacy
printf '%s\n' 'This report omits usernames, hostnames, process arguments, game paths, keys, saves, browser profiles, and Bluetooth identities.'
