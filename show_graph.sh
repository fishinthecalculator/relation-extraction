#!/usr/bin/env bash

if [[ "$#" -ne 2 ]]; then
	echo "Error: Too few arguments!"
	echo "Usage $(basename "$0") /path/to/rdf/file rdf-format."
	exit 1
fi

rdf=$(basename $1 | sed -E "s/\..*$//")

rapper -i "$2"  -o dot "$1" | dot -Tsvg -o"${rdf}.svg"
