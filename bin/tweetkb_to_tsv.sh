#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 1 ]] && echo "Usage $(basename "$0") /path/to/dir." && exit 1

tweets_dir="${1%/}"
entities_db_dir="${tweets_dir}/db"
tweet_ids="${entities_db_dir}/ids.tsv"

while read -r line;
do
    entity=$(printf "%s\n" "$line" | sed -E "s/(^.*_:| rdf:type.*)//g")

    tweet_id=$(printf "%s\n" "$entity" | sed -E "s/(e|_.*)//g")
    printf "%s\n" "$tweet_id"  >> "${tweet_ids}"

    uri=$(printf "%s\n" "$line" | sed -E "s/(.*<|>.*)//g")
    printf "%s\n" "$uri"  >> "${tweets_dir}/t${tweet_id}.tsv"

    token=$(printf "%s\n" "$line" | sed -E "s/^.+dAs \"(.+)\" ; nee:has.+$/\1/")

    printf "t%s\t%s\t%s\n" "${tweet_id}" "${uri}" "${token}" >> "${entities_db_dir}/tweets_and_entities.tsv" 
done
