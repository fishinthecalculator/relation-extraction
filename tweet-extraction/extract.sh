#!/usr/bin/env bash

mkdir -p tweets

get_URI () {
	rg "${1} rdf:type nee:Entity" first_10M_lines.n3 | sed -E "s/.*<//" | sed -E "s/>.*//"
}

process_tweet () {
	rg "${1}" tweets_and_entities.txt | cut -d " " -f 2 | while read ENTITY; do URI=$(get_URI "${ENTITY}"); echo "${ENTITY} ${URI}" >> "tweets/${1}.txt";  done
}


cat tweets_with_multiple_entities.txt | while read LINE; do process_tweet "${LINE}"; done

