#!/usr/bin/env python3
"""Preview or apply a conservative Linux laptop performance profile to Config.json."""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import pathlib
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("config", type=pathlib.Path)
parser.add_argument("--render-scale", type=float, default=0.75)
parser.add_argument("--vsync", choices=("keep", "on", "off"), default="keep")
parser.add_argument("--apply", action="store_true", help="write changes after creating a backup")
args = parser.parse_args()
if not 0.5 <= args.render_scale <= 2.0:
    parser.error("--render-scale must be between 0.5 and 2.0")

before_text = args.config.read_text()
before = json.loads(before_text)
after = dict(before)
after.update(
    graphics_backend="Vulkan",
    backend_threading="Auto",
    res_scale=-1,
    res_scale_custom=args.render_scale,
    max_anisotropy=-1,
    anti_aliasing="None",
    scaling_filter="Bilinear",
    docked_mode=False,
    enable_shader_cache=True,
    enable_macro_hle=True,
    enable_ptc=True,
    enable_low_power_ptc=False,
    tick_scalar=100,
)
if args.vsync != "keep":
    after["enable_vsync"] = args.vsync == "on"

after_text = json.dumps(after, indent=2, ensure_ascii=False) + "\n"
diff = "".join(
    difflib.unified_diff(
        before_text.splitlines(True), after_text.splitlines(True),
        fromfile=str(args.config), tofile=str(args.config) + " (proposed)",
    )
)
print(diff or "No changes needed.")
if args.apply and before_text != after_text:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = args.config.with_name(f"{args.config.name}.before-tuning-{stamp}")
    shutil.copy2(args.config, backup)
    args.config.write_text(after_text)
    print(f"Backup: {backup}")
    print(f"Updated: {args.config}")
elif not args.apply and before_text != after_text:
    print("Preview only. Re-run with --apply to write these changes.")
