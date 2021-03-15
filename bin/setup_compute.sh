#!/usr/bin/env bash
set -euo pipefail

set -x

remote_dir="${HOME}/remote"
tarball="$(basename "$(find "${remote_dir}/" -name "*.tar.gz" | head -1)")"


cd "${HOME}/.local/relext/"

find . -exec chmod 777 {} \;
find . -exec rm -rv {} \;

tar -xvf "${remote_dir}/${tarball}"
rm -rf "${remote_dir:?}/${tarball}"

exit 0
