#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 2 ]] && echo "Usage $(basename $0) /path/to/triples.n3 /path/to/dir." && exit 1

tweets_dir="${2%/}"

mkdir -p "${tweets_dir}"

rg "rdf:type nee:Entity" "${1}" | \
    parallel --pipe "$(dirname $0)/tweetkb_to_tsv.sh \"${tweets_dir}\""
