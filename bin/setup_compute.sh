#!/usr/bin/env bash
set -euo pipefail

set -x

remote_dir="${HOME}/remote"
thesis_dir="${HOME}/thesis"


rm -rf "${thesis_dir}/*.tar.gz"
mv "${remote_dir}/*.tar.gz" "${thesis_dir}/"

cd "${HOME}/.local/relext/"

chmod -R 777 ./*
rm -rf ./*

tar -xvf "$(find "$thesis_dir" -name "*.tar.gz" | head -1)"