#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
backend_dir="$script_dir/../elias-search-server"

if [[ $# -eq 0 ]]; then
  printf 'Usage: bash scripts/prepare_runtime_files.sh db.sqlite3|dj_log.log [...]\n' >&2
  exit 2
fi

# Check every path before creating anything. Never replace existing state.
for filename in "$@"; do
  case "$filename" in
    db.sqlite3|dj_log.log) ;;
    *) printf 'Unsupported runtime file: %s\n' "$filename" >&2; exit 2 ;;
  esac
  path="$backend_dir/$filename"
  if [[ -e "$path" || -L "$path" ]]; then
    if [[ ! -f "$path" || -L "$path" ]]; then
      printf 'Expected a regular runtime file: %s\nInspect and move the existing path aside before starting.\n' "$path" >&2
      exit 1
    fi
  fi
done

for filename in "$@"; do
  path="$backend_dir/$filename"
  if [[ ! -e "$path" ]]; then
    # noclobber also prevents overwriting a file created after the checks above.
    (umask 077; set -o noclobber; : > "$path")
    printf 'Created empty runtime file: %s\n' "$path"
  fi
done
