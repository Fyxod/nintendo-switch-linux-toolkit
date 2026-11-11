# Nintendo Switch Linux Toolkit

Practical tools and a reusable Codex skill for setting up, tuning, and troubleshooting Nintendo Switch games on Linux laptops, with a focus on **Pokémon Scarlet**, **Pokémon Violet**, and **Pokémon GO postcard connections**.

The toolkit brings together emulator launchers, configuration tuning, save backups, keyboard mappings, display recovery, and Bluetooth diagnostics. Pokémon Scarlet is the main worked example; the same workflow can be applied to Pokémon Violet while checking its exact game version and emulator build.

## What is included

- A [Codex skill](SKILL.md) with instructions for repeatable setup and troubleshooting.
- A Ryujinx-family launcher with NVIDIA PRIME offload, optional GameMode, and a temporary performance profile.
- Configuration tuning with a preview and a backup before changes.
- Save and configuration archives with a basic contents check.
- An X11 display wrapper that restores the previous layout after the game exits.
- Guidance for low FPS, shader stutter, blank scenes, camera controls, and thermal limits.
- Optional Pokémon GO postcard diagnostics and browser session management tools.

This repository contains tools and documentation. Supply your own authorized game dumps, updates, firmware, and keys, and install the emulator separately. Keep those files and all personal state outside the checkout.

## Get started

```bash
git clone https://github.com/Fyxod/nintendo-switch-linux-toolkit.git
cd nintendo-switch-linux-toolkit
./scripts/check-prerequisites.sh
```

The preflight reports available tools without installing packages or changing system settings.

### Requirements

| Component | Used for |
|---|---|
| Linux, Bash, Python 3.10+ | Core scripts |
| A compatible Ryujinx-family emulator | Running the game |
| Working Vulkan drivers | The documented graphics starting point |
| `xrandr` and an X11 session | Optional display scaling optimization |
| `powerprofilesctl`, `gamemoderun` | Optional power and process tuning |
| `nvidia-smi`, `vulkaninfo`, `sensors` | Optional GPU and thermal diagnostics |
| BlueZ, Python `dbus`, a Web Bluetooth browser | Optional Pokémon GO tools |
| Python `websocket` | Optional browser debugging monitor |

See [dependencies](references/dependencies.md) for package names and details. Game, emulator, and driver versions affect compatibility; check the documentation for the build you install.

### Use as a Codex skill

```bash
./scripts/install-skill.sh
```

This creates a symlink to the checkout in the Codex skills directory. Keep the checkout in place afterward. The installer refuses to overwrite an existing installation.

Example requests:

```text
Use $nintendo-switch-linux-toolkit to configure my Pokémon Scarlet dump on Linux.

Use $nintendo-switch-linux-toolkit to diagnose low FPS in Pokémon Violet.

Use $nintendo-switch-linux-toolkit to troubleshoot my Pokémon GO postcard connection.
```

The scripts can also be used directly, without installing the skill.

## Pokémon Scarlet and Pokémon Violet

### 1. Prepare the emulator

Install your emulator separately, provide the required firmware and keys, and add your game dump through its documented setup flow. Start the game once to confirm it boots and to create its configuration.

Keep the emulator data, game files, and backups outside this repository. The launcher accepts paths through environment variables; replace these example paths with your own:

```bash
export RYUJINX_BIN="/path/to/Ryujinx"
export RYUJINX_DATA_DIR="/path/to/emulator-data"
export SWITCH_GAME_FILE="/path/to/Pokemon-Scarlet.xci"
```

For Violet, point `SWITCH_GAME_FILE` at your Violet dump. Record the emulator version, game update, firmware version, and GPU driver when comparing results. A setting or patch for one build may behave differently on another.

### 2. Preserve progress

Save inside the game and wait for confirmation. Close the emulator before editing its configuration or archiving the save directory. Use the emulator's save-directory option to locate the correct title save.

```bash
python3 scripts/backup-state.py \
  --save-dir "/path/to/title-save-directory" \
  --config "$RYUJINX_DATA_DIR/Config.json" \
  --output-dir "/path/to/private-backups" \
  --label "pokemon-scarlet"
```

The archive includes the save directory and configuration. Keep it private and verify that it contains your expected save files.

### 3. Preview a performance profile

```bash
python3 scripts/tune-config.py "$RYUJINX_DATA_DIR/Config.json" \
  --render-scale 0.75
```

Review the proposed changes, then apply them:

```bash
python3 scripts/tune-config.py "$RYUJINX_DATA_DIR/Config.json" \
  --render-scale 0.75 --apply
```

The script creates a timestamped configuration backup before writing. Its starting profile uses Vulkan, backend threading `Auto`, handheld mode, shader cache, PPTC, bilinear scaling, and a normal tick scalar. VSync stays as configured unless you pass `--vsync on` or `--vsync off`.

The configuration keys match the Ryujinx-family build used for the documented workflow. Check your build's schema and the resulting emulator settings before relying on the profile.

### 4. Launch the game

```bash
USE_NATIVE_DISPLAY_SESSION=0 ./scripts/launch-ryujinx-linux.sh
```

The launcher selects NVIDIA offload when available and uses GameMode and a process-scoped performance profile when supported. It writes its launch log to `$XDG_STATE_HOME/nintendo-switch-linux-toolkit/last-launch.log`, or to the corresponding directory under `$HOME/.local/state` when `XDG_STATE_HOME` is unset. Override the location with `RYUJINX_LOG_PATH`.

The example disables display changes. On X11, the launcher otherwise enables its display wrapper by default. If fractional scaling is adding overhead, first inspect a proposed mode without applying it:

```bash
python3 scripts/display-session.py \
  --mode 1920x1080 --rate 60 --dry-run -- true
```

If your panel supports that mode and exactly one internal display is connected, enable it for the game:

```bash
USE_NATIVE_DISPLAY_SESSION=1 GAME_DISPLAY_MODE=1920x1080 GAME_DISPLAY_RATE=60 \
  ./scripts/launch-ryujinx-linux.sh
```

The wrapper restores the previous layout after exit if its temporary layout is still active. It leaves a display change made during the session alone. This optimization applies to X11; Wayland display management is outside the wrapper's scope.

### Keyboard controls

Configure these bindings in the emulator. The launcher does not install an input profile.

| Nintendo Switch input | Keyboard | Use in Scarlet/Violet |
|---|---|---|
| Left stick | `W A S D` | Movement |
| Right stick | `I J K L` | Camera |
| Right-stick click | `H` | Camera zoom/reset, where supported |
| A | `Z` | Confirm / interact |
| B | `X` | Cancel / back |
| X | `C` | Main menu |
| Y | `V` | Map / context action |
| L / ZL | `E` / `Q` | Shoulder inputs |
| R / ZR | `U` / `O` | Shoulder inputs |
| Plus | `Enter` | Plus / ride action |
| D-pad | Arrow keys | Navigation |

For the main menu, press keyboard **C**, which maps to Nintendo **X**. `Enter` maps to Plus. Vertical camera limits can be normal game behavior; unexpected horizontal limits call for checking the right-stick bindings, dead zones, and conflicting input devices.

## Performance expectations

The tuning examples aim for stable play around **30 FPS**. They do not include a 60 FPS patch. Assess any such patch against the exact game update and emulator build, and check that game timing remains correct.

The [field notes](references/field-notes.md) record one Scarlet session on a Linux Mint/X11 laptop with an RTX 3050 Laptop GPU:

| Observation | Approximate FPS |
|---|---:|
| Initial outdoor scene in power-saver mode | 14 |
| Same scene after switching to a performance profile | 19 |
| After combined graphics, cooling, power, and display tuning; stationary | 29–30 |
| Brief drops during rapid camera turns | 11–23 |

These are observations from one machine, not benchmarks for every laptop or an independently measured Violet result. Test the same outdoor scene while stationary and while moving the camera; a title-screen peak does not establish gameplay performance.

For low FPS, collect evidence before changing settings:

```bash
./scripts/collect-diagnostics.sh "$RYUJINX_DATA_DIR/Config.json"
```

Check AC power, the active power profile, CPU/GPU temperatures, the selected GPU, and display scaling. See [performance and recovery](references/performance-and-recovery.md) for interpreting those results and investigating blank or glitched scenes.

## Pokémon GO postcards and the Coin Bag

Sending a postcard to Pokémon Scarlet or Pokémon Violet unlocks or recharges Pokémon GO's Coin Bag, which attracts Roaming Form Gimmighoul. The official connection uses a phone and a compatible physical Nintendo Switch console running the game. Follow [Nintendo's pairing guide](https://en-americas-support.nintendo.com/app/answers/detail/a_id/61360/) and the [official Coin Bag explanation](https://pokemongo.com/news/gocoin).

### Official console connection

1. In GO, open **Settings → Connected Devices and Services → Nintendo Switch** and begin connecting.
2. In Scarlet or Violet, open **X → Poké Portal → Mystery Gift → Connect to Pokémon GO**, then pair with the GO account.
3. In GO's Postcard Book, select a postcard and choose the option to send it to Scarlet, Violet, or Nintendo Switch; the label can vary.
4. In the console game, return to **Connect to Pokémon GO**, then select **Communicate with Pokémon GO** to receive it.

Mystery Gift becomes available after reaching the first Pokémon Center in Los Platos. See [Nintendo's instructions](https://en-americas-support.nintendo.com/app/answers/detail/a_id/61360/) for the full prerequisites and current menu wording.

### Optional laptop helper

The emulator workflow documented here does not provide the phone-facing Bluetooth connection. The separate community project [pokemon-go-coin-bag](https://github.com/na-ji/pokemon-go-coin-bag) provides a web helper for the GO-side postcard exchange. Its protocol implementation is an external dependency.

Launch that helper with a persistent, dedicated browser profile:

```bash
BROWSER_BIN="/usr/bin/brave-browser" ./scripts/launch-coin-bag-helper.sh
```

Set `BROWSER_BIN` to your installed compatible browser. For Brave, the launcher adds the Web Bluetooth flags used in the documented session.

The [upstream helper workflow](https://github.com/na-ji/pokemon-go-coin-bag#how-to-use) has two separate Bluetooth connections:

1. Begin Switch pairing in GO, then use the helper to complete registration.
2. Begin sending a postcard in GO, then connect with the helper again to receive it.

Keep the browser profile between attempts: it stores the identity associated with the saved pairing. A disconnect after an operation can be normal. Confirm completion on the phone and check that the Coin Bag is available. The helper handles the GO exchange; it does not inject the postcard or its effects into an emulated Scarlet/Violet save.

For repeated searching or timeouts, the documented recovery was to force-stop GO, cycle phone Bluetooth, disconnect Bluetooth accessories, reopen GO, and retry with the existing pairing. See the [full postcard troubleshooting guide](references/pokemon-go-postcards.md) before resetting anything.

## Script reference

| Script | Purpose |
|---|---|
| [`check-prerequisites.sh`](scripts/check-prerequisites.sh) | Inventory host capabilities without changing settings |
| [`install-skill.sh`](scripts/install-skill.sh) | Link this checkout into the Codex skills directory |
| [`launch-ryujinx-linux.sh`](scripts/launch-ryujinx-linux.sh) | Launch a supplied game with optional GPU, power, and display tuning |
| [`tune-config.py`](scripts/tune-config.py) | Preview or apply a configuration profile with a backup |
| [`backup-state.py`](scripts/backup-state.py) | Archive a save directory and emulator configuration |
| [`display-session.py`](scripts/display-session.py) | Temporarily change an X11 internal-panel layout and restore it |
| [`collect-diagnostics.sh`](scripts/collect-diagnostics.sh) | Collect system data and selected emulator settings |
| [`launch-coin-bag-helper.sh`](scripts/launch-coin-bag-helper.sh) | Open the upstream web helper in a dedicated browser profile |
| [`coin-bag-probe.py`](scripts/coin-bag-probe.py) | Read-only BLE characteristic probe while the helper is idle |
| [`monitor-coin-bag-cdp.py`](scripts/monitor-coin-bag-cdp.py) | Start and monitor an attempt through a browser debugging session |
| [`fresh-device-session.js`](scripts/fresh-device-session.js) | Reusable session-ownership code for a Web Bluetooth UI |

The CDP monitor requires an already configured browser debugging session and its `DevToolsActivePort` file; the normal browser launcher does not enable debugging. The JavaScript module is an integration component, not a standalone postcard receiver. Run Python tools with `--help` for their options.

## Documentation

- [Skill instructions](SKILL.md)
- [Setup, controls, and save handling](references/setup-and-controls.md)
- [Dependencies](references/dependencies.md)
- [Performance and display recovery](references/performance-and-recovery.md)
- [Pokémon GO postcard troubleshooting](references/pokemon-go-postcards.md)
- [Measured results and field notes](references/field-notes.md)

## Privacy and license

Game files, firmware, keys, saves, logs, browser profiles, Bluetooth identities, and signing material are excluded from this repository. The diagnostics script omits common identifying fields; review any output before sharing it. Keep backups and emulator data in private directories outside the checkout.

The toolkit's original code and documentation are available under the [MIT License](LICENSE). External emulators and helpers retain their own licenses. Nintendo Switch and Pokémon names belong to their respective owners. This is an independent community project and is not affiliated with Nintendo or The Pokémon Company.
