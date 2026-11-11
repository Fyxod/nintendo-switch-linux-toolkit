# Dependencies and preflight

## Required base tools

The skill instructions and non-Bluetooth scripts assume Linux, Bash, Python 3.10 or newer, and standard GNU userland tools. X11 display wrapping additionally needs `xrandr`. The emulator and game inputs are deliberately not bundled.

Useful optional host tools are:

- `powerprofilesctl` for a process-scoped performance-profile hold.
- Feral GameMode and `gamemoderun` for process tuning.
- `vulkaninfo` from Vulkan Tools for renderer diagnostics.
- `nvidia-smi` on NVIDIA systems.
- `sensors` from lm-sensors for thermal readings.

Run `scripts/check-prerequisites.sh` for a read-only inventory. Package names vary by distribution; use the distribution's package manager and current documentation rather than pasting an unreviewed install command.

## Bluetooth diagnostics

The optional BLE tools need:

- BlueZ running on the host.
- Python D-Bus bindings (`python3-dbus` on Debian-family systems).
- Python WebSocket Client (`python3-websocket` on Debian-family systems) for the CDP monitor.
- Brave, Chromium, Chrome, or Edge with Web Bluetooth enabled.

`coin-bag-probe.py` imports only `dbus`. `monitor-coin-bag-cdp.py` imports both `dbus` and `websocket`. These packages are intentionally system dependencies rather than vendored code because D-Bus bindings must match the host Python/GLib environment.

The community web helper is an upstream dependency, not part of this repository: <https://github.com/na-ji/pokemon-go-coin-bag>. Its protocol/signing implementation and saved browser identity are not copied here.

## Emulator and browser checks

Before launching:

1. Verify the emulator executable and its release source.
2. Supply only a game dump, firmware, and keys that the user is authorized to use.
3. Keep those inputs outside this repository.
4. For Bluetooth, confirm that exactly one adapter is available and disconnect unrelated phone accessories when diagnosing GATT timeouts.
5. Use a dedicated browser profile and retain it between pairing and postcard exchange.

The scripts avoid automatic package installation so running the preflight cannot alter the host or silently add third-party repositories.
