#!/usr/bin/env python3
"""Archive an emulator save directory and configuration outside the game tree."""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--save-dir", required=True, type=pathlib.Path)
parser.add_argument("--config", required=True, type=pathlib.Path)
parser.add_argument("--output-dir", required=True, type=pathlib.Path)
parser.add_argument("--label", default="switch-game")
args = parser.parse_args()
if not args.save_dir.is_dir():
    parser.error(f"save directory does not exist: {args.save_dir}")
if not args.config.is_file():
    parser.error(f"configuration does not exist: {args.config}")
safe_label = "".join(character for character in args.label if character.isalnum() or character in "-_").strip("-_")
if not safe_label:
    parser.error("--label must contain a letter or number")
save_root = args.save_dir.resolve()
output_root = args.output_dir.resolve()
if output_root == save_root or save_root in output_root.parents:
    parser.error("--output-dir must be outside --save-dir")
args.output_dir.mkdir(parents=True, exist_ok=True)
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
archive = args.output_dir / f"{safe_label}-{stamp}.tar.gz"
with tarfile.open(archive, "x:gz") as bundle:
    bundle.add(args.save_dir, arcname="save", recursive=True)
    bundle.add(args.config, arcname="Config.json", recursive=False)
with tarfile.open(archive, "r:gz") as bundle:
    members = bundle.getmembers()
if not any(member.isfile() and member.name.startswith("save/") for member in members):
    archive.unlink()
    raise SystemExit("archive verification failed: no save files were added")
print(archive)
