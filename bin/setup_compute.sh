#!/usr/bin/env bash
set -euo pipefail

set -x

remote_dir="${HOME}/remote"
thesis_dir="${HOME}/thesis"


rm -rf "${thesis_dir}/*.tar.gz"
mv "${remote_dir}/*.tar.gz" "${thesis_dir}/"