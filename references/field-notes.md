# Field notes: findings worth preserving

These observations came from one Linux Mint/X11 laptop with an Intel hybrid CPU, an RTX 3050 Laptop GPU, fractional scaling, and a Ryujinx-family build. Treat numbers as evidence from that machine, not universal guarantees.

## Performance progression

- Initial outdoor performance was about 14 FPS.
- The laptop was plugged in but set to `power-saver`. A performance profile raised the same scene to roughly 19 FPS.
- CPU temperature approached 95–96°C and the GPU reached its 87–89°C target with software thermal slowdown. Cooling was a limiting factor.
- A supported custom fan curve, handheld mode, 0.75 render scale, Vulkan, backend threading `Auto`, reality tick scalar, GameMode, and a per-process performance hold produced roughly 29–30 FPS while stationary in the same area.
- Quick 360° camera turns still caused short drops near 11–23 FPS while assets streamed; recovery returned toward 30 FPS.
- The original Switch target for this game is 30 FPS. A measured 29–30 at rest is successful tuning, not a locked 30 under every camera movement.

## Display scaling

The 1920×1080 panel was exposed as a 3072×1728 X11 framebuffer through a 1.6 transform. Temporarily using native 1920×1080 at 60 Hz reduced composition overhead. Restoring the original transform and framebuffer after exit was essential.

An output name can change across GPU/session transitions (`eDP-1-1`, `eDP-1-2`, and similar). Discover the currently connected internal output; never hard-code it.

## Failed graphics experiment

Turning Vulkan backend threading `Off` briefly showed the target FPS but later crashed in the NVIDIA driver (`libnvidia-glcore`). The stable final choice was `Auto`. Preserve crash evidence in a local log, then restore the stable setting.

OpenGL was queued as a comparison but not established as better. Do not inherit it as a default from an interrupted test. Vulkan remained the known-good final backend.

## Visual failure that looked worse than it was

A scene with audio but no usable world view was caused by presentation/camera state rather than demonstrated GPU damage. Moving forward, rotating the camera, adjusting zoom, and reducing the oversized window restored the world. Avoid declaring hardware failure from one emulator scene.

## Controller lessons

- Nintendo X opened the Pokémon main menu; Plus did not.
- Keyboard `C` mapped to Nintendo X, `V` to Y, and `Enter` to Plus.
- `J`/`L` were right-stick horizontal camera controls. Normal vertical pitch limits were game behavior; a horizontal stop would have indicated a mapping problem.

## Bluetooth lessons

- A green “Switch paired” state represented successful registration and still functioned as the connection button in the upstream UI; this was confusing.
- Pairing and sending required two separate BLE connections.
- Restarting or reloading the helper during a live connection caused avoidable failure and user frustration. Monitor first; do not reset a live session.
- The stored browser application identity represented the saved Switch pairing. Temporary GATT state could be reset without deleting it.
- The repeated phone failure occurred on the first readable protocol characteristic after service discovery. A native BlueZ read reproduced ATT `0x0e` after 30 seconds, proving it was below the browser layer. Force-stopping GO and cycling phone Bluetooth resolved it; the subsequent exchange completed every stage.

## Completion hygiene

Before closing the emulator, an in-game save was confirmed visually and its save files were archived. Configuration and fan-curve backups were stored separately. This avoided turning an optimization experiment into lost progress.
