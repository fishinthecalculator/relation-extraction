#!/usr/bin/env bash

set -euo pipefail

HERE=$(dirname "$0")

TOKEN=" "

for tweet in "${HERE}"/tweet-extraction/related/*.txt;
do
    id=$(echo "$tweet" | sed -E "s/.*t(.*)\.txt/\1/")
    rg "$id.* rdf:type nee:Entity ; nee:detectedAs" "${HERE}/tweet-extraction/first_10M_lines.n3" | \
        sed -E "s/.*dAs \"//" | \
        sed -E "s/confidence.*//" | \
        sed -E "s/\".*//" | \
        sed -E "s/${TOKEN}/\n/g"
done
