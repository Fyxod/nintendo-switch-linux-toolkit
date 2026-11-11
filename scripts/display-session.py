#!/usr/bin/env python3
"""Run one command with an X11 internal panel at native scale, then restore it."""
from __future__ import annotations

import argparse
import dataclasses
import re
import signal
import subprocess
import sys


@dataclasses.dataclass(frozen=True)
class DisplayState:
    output: str
    mode: str
    rate: str
    framebuffer: str
    transform: tuple[str, ...]


def xrandr_text() -> str:
    return subprocess.check_output(["xrandr", "--verbose"], text=True)


def state_from_xrandr(text: str) -> DisplayState | None:
    screen = re.search(r"current (\d+) x (\d+)", text)
    connected = re.findall(r"^(\S+) connected[^\n]*$", text, re.MULTILINE)
    internal = [name for name in connected if name.startswith(("eDP", "LVDS"))]
    if not screen or len(connected) != 1 or len(internal) != 1:
        return None
    output = internal[0]
    header = re.search(rf"^{re.escape(output)} connected[^\n]*$", text, re.MULTILINE)
    if not header:
        return None
    next_header = re.search(r"^\S+ (?:connected|disconnected)[^\n]*$", text[header.end():], re.MULTILINE)
    end = header.end() + (next_header.start() if next_header else len(text[header.end():]))
    block = text[header.start():end]
    mode = re.search(
        r"^\s+(\S+) \([^\n]+\*current[^\n]*\n[^\n]*\n[^\n]*clock\s+([\d.]+)Hz",
        block,
        re.MULTILINE,
    )
    transform = re.search(
        r"Transform:\s+([^\n]+)\n\s+([^\n]+)\n\s+([^\n]+)", block
    )
    if not mode or not transform:
        return None
    matrix = tuple(" ".join(transform.groups()).split())
    if len(matrix) != 9:
        return None
    return DisplayState(
        output=output,
        mode=mode.group(1),
        rate=mode.group(2),
        framebuffer="x".join(screen.groups()),
        transform=matrix,
    )


def read_state() -> DisplayState | None:
    return state_from_xrandr(xrandr_text())


def apply_native(state: DisplayState, mode: str, rate: str) -> None:
    subprocess.run(
        [
            "xrandr", "--output", state.output, "--mode", mode, "--rate", rate,
            "--scale", "1x1", "--fb", mode,
        ],
        check=True,
    )


def restore(state: DisplayState) -> None:
    subprocess.run(
        [
            "xrandr", "--output", state.output, "--mode", state.mode,
            "--rate", state.rate, "--transform", ",".join(state.transform),
            "--fb", state.framebuffer,
        ],
        check=True,
    )


def is_installed_layout(state: DisplayState | None, mode: str, rate: str) -> bool:
    if state is None:
        return False
    identity = ("1.000000", "0.000000", "0.000000", "0.000000", "1.000000",
                "0.000000", "0.000000", "0.000000", "1.000000")
    return (
        state.mode == mode
        and state.framebuffer == mode
        and abs(float(state.rate) - float(rate)) < 1.0
        and state.transform == identity
    )


parser = argparse.ArgumentParser()
parser.add_argument("--mode", default="1920x1080")
parser.add_argument("--rate", default="60")
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
if args.command[:1] == ["--"]:
    args.command = args.command[1:]
if not args.command:
    parser.error("provide a command after --")

original = read_state()
if original is None:
    print("Display optimization skipped: expected exactly one connected internal panel.", flush=True)
    if args.dry_run:
        sys.exit(0)
    sys.exit(subprocess.call(args.command))

print(
    f"Display session: {original.output} {original.mode}@{original.rate}, "
    f"framebuffer {original.framebuffer} -> {args.mode}@{args.rate} native",
    flush=True,
)
if args.dry_run:
    sys.exit(0)

changed = False
child: subprocess.Popen[bytes] | None = None
status = 1
try:
    apply_native(original, args.mode, args.rate)
    changed = True
    child = subprocess.Popen(args.command)

    def forward(sig: int, _frame: object) -> None:
        if child and child.poll() is None:
            child.send_signal(sig)

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    status = child.wait()
finally:
    # Restore only our exact temporary layout. This avoids overwriting a display
    # change or newly attached monitor chosen by the user during the session.
    if changed and is_installed_layout(read_state(), args.mode, args.rate):
        restore(original)
        print("Desktop display restored.", flush=True)

sys.exit(128 - status if status < 0 else status)
