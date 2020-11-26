#!/usr/bin/env bash

set -euo pipefail

[[ "$#" -ne 2 ]] && echo "$@" && echo "Usage: $(basename $0) /path/to/entities.tsv /out/dir/path" && exit 1

entities="$1"

tweets_dir="${2%/}"

mkdir -p "$tweets_dir"

cut -f 1 "$entities" | \
	sort | \
	uniq -d | \
	while read -r tweet;
	do
		rg "$tweet" "$entities" | cut -f 3 > "$tweets_dir/$tweet.txt"
	done
