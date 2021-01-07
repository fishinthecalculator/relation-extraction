#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 1 ]] && echo "Usage $(basename "$0") /path/to/dir." && exit 1

tweets_dir="${1%/}/entities"

while read -r line;
do
    entity=$(printf "%s\n" "$line" | sed -E "s/(^.*_:| rdf:type.*)//g")

    tweet_id=$(printf "%s\n" "$entity" | sed -E "s/(e|_.*)//g")
    printf "%s\n" "$tweet_id"

    uri=$(printf "%s\n" "$line" | sed -E "s/(.*<|>.*)//g")

    token=$(printf "%s\n" "$line" | sed -E "s/^.+dAs \"(.+)\" ; nee:has.+$/\1/")

    printf "%s\t%s\n" "${uri}" "${token}" >> "${tweets_dir}/t${tweet_id}.tsv"
done

exit 0
