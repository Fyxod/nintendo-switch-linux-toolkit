# Performance and display recovery

## Establish the target

Verify the native target of the specific game. Pokémon Scarlet/Violet on the original Switch targets 30 FPS and often falls below it; 60 FPS is not the baseline target. A 60 FPS patch can alter timing, physics, or stability and must be verified for the exact title ID and game version.

Measure a repeatable scene for at least several samples. Report an FPS range and frame time. Menu/title-screen FPS is not representative of a busy outdoor scene.

## First-pass diagnostics

Collect:

```bash
powerprofilesctl get
nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,clocks.gr,pstate --format=csv
sensors
free -h
uptime
ps -eo pid,comm,%cpu,%mem,rss --sort=-%cpu | head
xrandr --query
```

Interpret together:

- Low GPU utilization plus one saturated emulator thread usually indicates CPU/emulation limits.
- A GPU at its target temperature with software thermal slowdown indicates a thermal ceiling even if utilization is not 100%.
- A `power-saver` profile while plugged in can reduce FPS substantially.
- High unrelated CPU or I/O activity can produce stutter. Identify the process before stopping it.
- On X11 fractional scaling, a physical 1920×1080 panel may expose a 3072×1728 framebuffer with a 1.6 transform. Fullscreen composition at that logical size can cost performance.

## Known-good Ryujinx direction for a 4 GB laptop GPU

Start with:

- Vulkan and the discrete GPU explicitly selected.
- Graphics backend multithreading `Auto` or `On`.
- Handheld mode for a 720p internal target.
- Shader cache and PPTC enabled.
- Anti-aliasing off, bilinear scaling, automatic anisotropic filtering.
- Host-mapped memory mode if supported and stable.
- VSync off while measuring; restore it if tearing matters after reaching the target.
- Clock/tick scalar at reality speed (`100` in builds where 100 means 1.0). Do not use the turbo scalar as a performance fix.

For a thermally constrained 1080p laptop, a custom render scale around `0.75` can materially improve performance. Check image quality and text readability. Texture recompression can help low VRAM systems but may introduce visual artifacts, so test it rather than enabling it blindly.

Backend threading `Off` is a useful comparison only when safe to restart. In one NVIDIA Linux session it reached the target briefly and then segfaulted inside `libnvidia-glcore`; `Auto` was stable and therefore the correct final setting.

## Power and cooling

Use `powerprofilesctl launch --profile performance ...` so the profile hold ends with the game. Use GameMode if available. Avoid leaving the whole desktop in performance mode after the game closes.

Custom fan curves can improve sustained clocks on supported ASUS laptops, but model support and safe ranges differ. Read the existing curve first, back it up, and use `asusctl` only when the hardware reports fan-curve support. Never assume values from another laptop are safe.

Temperatures near the CPU's critical threshold or the GPU's target temperature explain falling clocks. Higher fan speed cannot compensate for blocked vents, dust, failed fans, or dried thermal compound. Do not increase power limits on a system already thermally throttling.

## Display-session optimization

On a fractionally scaled X11 desktop, temporarily running the internal panel at native physical resolution and 60 Hz can reduce compositor work. `scripts/display-session.py` records the original mode, transform, framebuffer, and refresh rate; applies native rendering for the child command; then restores the original state.

Apply this only when exactly one internal display is connected. If a monitor is attached or the user changes the display while playing, leave the new layout alone. Always provide a dry run.

Fullscreen may help when the compositor can unredirect it. A smaller non-maximized window may perform better on some drivers. Measure both; do not assume fullscreen is faster.

## Black, glitched, or invisible world

Audio with a corrupt or blank scene does not prove GPU failure. Check, in order:

1. Is the emulator responsive and still presenting frames?
2. Does `nvidia-smi` show the expected process on the discrete GPU?
3. Did the window open at an extreme size or under fractional scaling?
4. Is the camera clipped inside the avatar, a wall, or a building? Move forward and rotate/zoom the camera.
5. Is shader/PPTC compilation still running?
6. Does a smaller window restore the scene?
7. Are there Vulkan, NVIDIA Xid, segfault, or out-of-memory messages in the current log and kernel journal?

Back up the save, then restart the emulator gracefully if necessary. A forced laptop shutdown is not evidence that the GPU is damaged. Hardware damage needs independent evidence such as persistent artifacts across applications, driver initialization failures, or diagnostic errors.

## Completion check

Test the same outdoor scene at rest and during camera rotation. Camera rotation streams new assets and is often the worst case. A result such as 29–30 FPS at rest with short drops during turns is materially different from a locked 30 FPS; report that distinction.
