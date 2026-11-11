# Setup, controls, and save handling

## Installation inputs

Require the user to provide:

- A legally obtained game dump (`.xci`, `.nsp`, or another emulator-supported format).
- Firmware and keys dumped from hardware they own when the emulator requires them.
- Any game update or DLC they are authorized to use.

Use current emulator documentation instead of relying on a stale download URL. At the time this guide was written, maintained Ryujinx-family documentation is available at <https://docs.ryujinx.app/> and current builds at <https://www.ryujinx.dev/download.html>. Verify these again before installation because emulator projects and maintainers can change.

Do not put the emulator inside a game repack directory. A portable layout makes rollback and removal clearer:

```text
switch-lab/
|-- emulator/
|   |-- Ryujinx
|   `-- portable/          # emulator configuration and user data
|-- games/                 # user-supplied dumps; never commit
|-- backups/
|-- logs/
`-- launch.sh
```

Install the firmware and keys through the emulator UI or documented filesystem locations. Confirm that the game is recognized before applying performance settings.

## Launcher design

Use a dedicated user-data directory so the setup is reproducible and does not collide with another emulator installation. A useful launcher should:

- Lock itself so repeated clicks focus the existing emulator instead of starting a second copy.
- Check that the emulator and selected game file exist.
- Select the discrete GPU on hybrid NVIDIA laptops with PRIME variables.
- Request a performance profile only for the process lifetime.
- Use GameMode when installed.
- Write a fresh launch log to a predictable location.
- Restore temporary display changes on process exit.

See `scripts/launch-ryujinx-linux.sh` and `scripts/display-session.py`.

## Reliable keyboard map

Use Nintendo button names in the emulator and document their keyboard equivalents:

| Switch input | Keyboard | Typical use |
|---|---:|---|
| Left stick | `W A S D` | Movement |
| Right stick | `I J K L` | Camera |
| Right-stick click | `H` | Camera zoom/reset in supported games |
| A | `Z` | Confirm/interact |
| B | `X` | Cancel/back |
| X | `C` | Main menu in Pokémon Scarlet/Violet |
| Y | `V` | Map/context action |
| L / ZL | `E` / `Q` | Shoulder inputs |
| R / ZR | `U` / `O` | Shoulder inputs |
| Plus | `Enter` | Ride/Plus action; not the Pokémon main menu |
| D-pad | Arrow keys | Menu/navigation |

The keyboard letter and Nintendo label are different layers. If the user says “menu button,” confirm the in-game control rather than assuming `Enter`: Pokémon Scarlet/Violet opens its main menu with Nintendo **X**, mapped above to `C`.

If camera movement stops at a normal pitch limit but pans left/right continuously, that is game behavior. If horizontal movement also stops early, inspect right-stick dead zones, axis bindings, keyboard rollover, and whether a mouse or another controller is also mapped.

## Save discipline

Before risky changes:

1. Save inside the game and wait for its success message.
2. Locate the emulator's per-title save directory from the UI when possible.
3. Archive the save directory and configuration separately with a timestamp.
4. Verify that the archive contains the expected files and that their modification times match the save.

Do not infer a valid save from the emulator window closing cleanly. Do not copy the save into a public repository.

## Updates and version mismatch

Record the base game version, installed update version, firmware version, emulator version, and GPU driver in diagnostics. Features added after release may simply be absent from an old game build. Do not misdiagnose a missing feature as a control or Bluetooth fault.
