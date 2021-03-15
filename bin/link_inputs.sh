#!/usr/bin/env bash
set -euo pipefail

[ $# -eq 0 ] && echo "Usage $(basename "$0") dataset1 dataset2 ..." && exit 1

for arg in "$@"; do
    dataset="$(basename "$arg")"
    inputs_dir="$(dirname "$arg")/../inputs"
    input="$(realpath "${inputs_dir}/${dataset}")"
    if [ ! -e "$input" ]; then
        ln -s "$(realpath "${arg}")" "${input}"
    else
        echo "Warning: ${input} already exists..."
    fi
done

exit 0
