#!/usr/bin/env bash
set -euo pipefail

set -x

remote_dir="${HOME}/remote"
tarball="$(basename "$(find "${remote_dir}/" -name "*.tar.gz" | head -1)")"


bindir="${HOME}/.local/relext/"

cd "$bindir"

export PATH="/vol/local/bin:/usr/local/bin:/usr/bin:/bin:/usr/games:/vol/local/bin:/usr/local/bin:/usr/bin:/bin:/usr/games:/usr/local/bin:/usr/bin:/bin:/usr/games"

find "$bindir" -type f | while read -r f; do
    chmod +w "$f" "$(dirname "$f")"
    rm -vrf "$f"
done

tar -xvf "${remote_dir}/${tarball}" > tar-messages.log 2> tar-errors.log; rm -rf "${remote_dir:?}/${tarball}"

exit 0
