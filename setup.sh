#!/bin/sh
set -eu
studio_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 -m venv "$studio_dir/.venv"
"$studio_dir/.venv/bin/python" -m pip install --index-url https://pypi.org/simple --timeout 15 --retries 1 -r "$studio_dir/requirements.txt"
printf '\nReady. Run: ./draw.sh line\n'
