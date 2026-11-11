#!/usr/bin/env bash
set -euo pipefail

required=(bash python3)
optional=(xrandr powerprofilesctl gamemoderun vulkaninfo nvidia-smi sensors bluetoothctl)
missing_required=0

printf '%s\n' '[required]'
for tool in "${required[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf 'ok      %s\n' "$tool"
  else
    printf 'missing %s\n' "$tool"
    missing_required=1
  fi
done

printf '%s\n' '[optional]'
for tool in "${optional[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf 'ok      %s\n' "$tool"
  else
    printf 'absent  %s\n' "$tool"
  fi
done

printf '%s\n' '[python Bluetooth modules]'
python3 - <<'PY'
import importlib.util

for module in ("dbus", "websocket"):
    state = "ok" if importlib.util.find_spec(module) else "absent"
    print(f"{state:7} {module}")
PY

if [[ -r /sys/class/power_supply/AC/online ]]; then
  printf 'AC online: %s\n' "$(</sys/class/power_supply/AC/online)"
fi
exit "$missing_required"
