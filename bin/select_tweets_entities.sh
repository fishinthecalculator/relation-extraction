#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 2 ]] && echo "Usage $(basename "$0") /path/to/triples.n3 /path/to/results." && exit 1

results_dir="${2%/}"
ids="${results_dir}/tweets/ids.tsv"

echo "Saving ids to ${ids}..."

rg "rdf:type nee:Entity" "${1}" | \
    parallel -N1 --linebuffer --roundrobin --pipe "$(dirname "$0")/tweetkb_to_tsv.sh \"${results_dir}\"" | \
    tee /dev/fd/2 | \
    sort -n -u > "${ids}"

exit 0
