#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 1 ]] && echo "Usage $(basename $0) /path/to/dir." && exit 1

tweets_dir="${1%/}"
entities_db_dir="${tweets_dir}/db"

mkdir -p "${entities_db_dir}"

while read -r line;
do
    entity=$(echo "$line" | sed -E "s/(^.*_:| rdf:type.*)//g")

    tweet_id=$(echo "$entity" | sed -E "s/(e|_.*)//g")

    uri=$(echo "$line" | sed -E "s/(.*<|>.*)//g")

    token=$(echo "$line" | sed -E "s/^.+dAs (.+) ; nee:has.+$/\1/")

    echo -e "t${tweet_id}\t${entity}\t${uri}\t${token}" | \
        tee -a "${entities_db_dir}/tweets_and_entities.tsv" | \
        cut -f 3 >> "${tweets_dir}/t${tweet_id}.tsv"
done
