#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
skills_root="${CODEX_HOME:-$HOME/.codex}/skills"
target="$skills_root/nintendo-switch-linux-toolkit"
mkdir -p -- "$skills_root"
if [[ -L "$target" ]] && [[ "$(readlink -f -- "$target")" == "$repo_root" ]]; then
  printf 'Already installed: %s\n' "$target"
  exit 0
fi
if [[ -e "$target" || -L "$target" ]]; then
  printf 'Refusing to replace existing path: %s\n' "$target" >&2
  exit 1
fi
ln -s -- "$repo_root" "$target"
printf 'Installed skill: %s -> %s\n' "$target" "$repo_root"
