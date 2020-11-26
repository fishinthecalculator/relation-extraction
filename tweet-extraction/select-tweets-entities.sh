#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 1 ]] && echo "Usage $(basename $0) /path/to/triples.n3." && exit 1

rg "rdf:type nee:Entity" "${1}" | while read -r line;
do
    entity=$(echo "$line" | sed -E "s/(_:| rdf:type.*)//g")
    tweet_id=$(echo "$entity" | sed -E "s/(e|_.*)//g")
    uri=$(echo "$line" | sed -E "s/(.*<|>.*)//g")
    token=$(echo "$line" | sed -E "s/^.+dAs \"(.+)\" ;.+$/\1/")
    echo -e "t${tweet_id}\t${entity}\t${uri}\t${token}"
done
