#!/usr/bin/env bash
set -euo pipefail

set -x

remote_dir="${HOME}/remote"
tarball="$(basename "$(find "${remote_dir}/" -name "*.tar.gz" | head -1)")"


bindir="${HOME}/.local/relext/"

cd "$bindir"

find "$bindir" -type f | while read -r f; do
    chmod +w "$f" "$(dirname "$f")"
    rm -vrf "$f"
done

tar -xvf "${remote_dir}/${tarball}"
rm -rf "${remote_dir:?}/${tarball}"

exit 0
