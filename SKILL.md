---
name: nintendo-switch-linux-toolkit
description: Configure, optimize, and troubleshoot legally dumped Nintendo Switch games in Ryujinx-compatible emulators on Linux laptops, including controller mapping, save-safe display recovery, GPU and thermal diagnosis, and optional Pokémon GO postcard Bluetooth troubleshooting. Use for hands-on Linux emulator setup and repair; do not use to acquire games, firmware, encryption keys, or copyrighted assets.
---

# Nintendo Switch Linux Toolkit

Help the user reach a playable, repeatable setup while preserving saves and existing pairings.

## Boundaries

- Work only with games, updates, firmware, and keys the user is authorized to use and has supplied from their own hardware or another lawful source.
- Do not search for, download, extract, upload, or redistribute ROMs, repacks, firmware, title keys, prod keys, signing material, save files, or account data.
- Treat third-party packages as untrusted. Prefer current project documentation, checksums, and reputable release sources.
- Keep game files, firmware, keys, logs, browser profiles, saves, and Bluetooth identities out of repositories and shared diagnostics.
- Explain when behavior comes from the original game, the emulator, the graphics driver, or an unofficial helper. Do not present inference as proof.

## Working method

1. Inspect the machine before changing it: OS/session type, CPU, GPUs, driver, RAM, AC power, power profile, temperatures, fans, display mode/scaling, emulator process load, and the relevant emulator settings.
2. Back up the emulator configuration and save directory before changes that require a restart, cache reset, or format conversion. Never clear a browser profile or saved Bluetooth identity to fix a temporary connection unless the user explicitly asks to re-pair.
3. Make one meaningful change at a time and measure the same scene or failure stage. Preserve a known-good rollback.
4. Prefer reversible settings and per-launch wrappers over permanent global changes. Restore display and desktop settings after the emulator exits.
5. Confirm the final state from observable evidence: stable FPS samples, a rendered scene, a current log, a phone-side success message, or a save timestamp. Close the emulator only after an in-game save and backup when the user asks.

## Route the task

- For installation, portable layouts, launch wrappers, controller mapping, and save handling, read [references/setup-and-controls.md](references/setup-and-controls.md).
- For host packages, browser requirements, and an installation preflight, read [references/dependencies.md](references/dependencies.md).
- For low FPS, thermal throttling, black/glitched scenes, driver failures, or display scaling, read [references/performance-and-recovery.md](references/performance-and-recovery.md).
- For Pokémon GO postcards or Coin Bag connection problems, read [references/pokemon-go-postcards.md](references/pokemon-go-postcards.md).
- For the high-value findings and failed approaches from a real Linux laptop session, read [references/field-notes.md](references/field-notes.md).

## Reusable scripts

- Run `scripts/check-prerequisites.sh` before setup to inventory required and optional host capabilities without changing the machine.
- Run `scripts/install-skill.sh` to install this checkout into the local Codex skills directory as a symlink.
- Run `scripts/collect-diagnostics.sh [Config.json]` for a privacy-conscious system and emulator summary.
- Run `scripts/tune-config.py Config.json` to preview conservative settings; add `--apply` only after reviewing the diff. It creates a timestamped backup.
- Run `scripts/backup-state.py --save-dir PATH --config Config.json --output-dir PATH` before a risky restart or configuration experiment.
- Adapt `scripts/launch-ryujinx-linux.sh` as a launcher. It uses environment variables, requests a temporary performance profile, supports NVIDIA PRIME offload, and can wrap the game with native display rendering.
- Use `scripts/display-session.py --dry-run -- true` to inspect its proposed display change. With a real command, it switches one internal panel to native resolution for the process and restores the prior layout on exit.
- Use `scripts/coin-bag-probe.py` only when the web helper is idle and the phone is already searching. It performs read-only BLE diagnostics and never writes pairing or postcard data.
- Use `scripts/launch-coin-bag-helper.sh` for a persistent, dedicated browser profile. `scripts/monitor-coin-bag-cdp.py --select-single` can monitor a user-requested attempt and select only one unambiguous filtered device.
- Use `scripts/fresh-device-session.js` as the session-ownership pattern when adding a “connect another device” button to a Web Bluetooth UI.

## Finish cleanly

Report what changed, why it helped, how it was measured, the achieved range rather than a single peak, and remaining limits. Link local backups or edited launchers when available. Avoid promising 60 FPS for a game whose original target is 30 FPS unless a verified game-specific update or mod is in scope and tested.
