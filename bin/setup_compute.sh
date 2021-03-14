#!/usr/bin/env bash
set -euo pipefail

set -x

remote_dir="${HOME}/remote"
thesis_dir="${HOME}/thesis"
tarball="$(basename "$(find "$remote_dir" -name "*.tar.gz" | head -1)")"

rm -rf "${thesis_dir}/"*.tar.gz
mv "${remote_dir}/${tarball}" "${thesis_dir}/"

cd "${HOME}/.local/relext/"

chmod -R 777 ./*
rm -rf ./*

tar -xvf "${thesis_dir}/${tarball}"
