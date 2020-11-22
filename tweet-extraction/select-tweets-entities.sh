#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 1 ]] && echo "Usage $(basename $0) /path/to/triples.nt" && exit 1

rg "rdf:type nee:Entity" "${1}" | while read -r line;
do
    entity=$(echo "$line" | sed -E "s/(_:| rdf:type.*)//g")
    tweet_id=$(echo "$entity" | sed -E "s/(e|_.*)//g")
    uri=$(echo "$line" | sed -E "s/(.*<|>.*)//g")
    echo -e "t${tweet_id}\t$entity\t$uri"
done
