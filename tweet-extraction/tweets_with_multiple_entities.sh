#!/usr/bin/env bash

[[ "$#" -ne 2 ]] && echo "Usage: $(basename $0) /path/to/entities.tsv /out/dir/path" && exit 1

entities="$1"

tweets_dir="${2%/}"

[[ ! -d "$2" ]] && echo "$2 is not a directory!" && exit 1

mkdir -p "$tweets_dir"

awk -F '\t' '{ print $1 }' "$entities" | \
	sort | \
	uniq -d | \
	while read -r tweet;
	do
		rg "$tweet" "$entities" | sed -E "s/${tweet}\t//" >> "$tweets_dir/$tweet.txt"
	done
