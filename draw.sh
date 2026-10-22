#!/bin/sh
set -eu
studio_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$#" -eq 0 ]; then
    printf 'Usage: ./draw.sh EXAMPLE [plot options]\nExample: ./draw.sh line --y-min 0.2\n'
    exit 1
fi
figure=$1
shift
case "$figure" in
    ''|*[!a-zA-Z0-9_-]*) printf 'Use a simple example name, such as line.\n' >&2; exit 1 ;;
esac
plot_file="$studio_dir/examples/$figure/plot.py"
if [ ! -f "$plot_file" ]; then
    printf 'Figure script not found: %s\n' "$plot_file" >&2
    exit 1
fi
if [ ! -x "$studio_dir/.venv/bin/python" ]; then
    printf 'Run ./setup.sh first.\n' >&2
    exit 1
fi
exec "$studio_dir/.venv/bin/python" "$plot_file" "$@"
