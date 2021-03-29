HERE=$(shell pwd)

ARCHIVE=${HERE}/archive
DATASETS=${HERE}/datasets
INPUTS=${HERE}/inputs
RESULTS=${HERE}/results

# Workflow inputs
UBY=${INPUTS}/uby
TWEETSKB=${INPUTS}/tweetskb
DBPEDIA=${INPUTS}/dbpedia

# Original datasets
UBY_DATA=${DATASETS}/uby
TWEETSKB_DATA=${DATASETS}/tweetskb
DBPEDIA_DATA=${DATASETS}/dbpedia

N_LINES=500000


all: fim

setup:
	bin/link_inputs.sh "${UBY_DATA}" "${TWEETSKB_DATA}" "${DBPEDIA_DATA}"

graph:
	guix workflow graph run.w | dot -Tsvg -o run.svg

bags: graph setup
	guix workflow run workflows/feature-extraction.w

fim: bags
	guix workflow run workflows/fim.w

test: graph setup
	mkdir -p "${INPUTS}"

	head -n ${N_LINES} "${TWEETSKB_DATA}" > "${TWEETSKB}"
	head -n ${N_LINES} "${DBPEDIA_DATA}" > "${DBPEDIA}"

	guix workflow run workflows/feature-extraction.w
	guix workflow run workflows/fim.w

scrape:
	tweet_text.py -i "${RESULTS}/tweets" -o "${RESULTS}/tweets"

compress:
	tar -cf "${ARCHIVE}"/$(shell date +%Y-%m-%d+%H.%M)-$(shell git log | head -1 | cut -d " " -f 2).tar.bz2 --use-compress-prog=pbzip2 "${RESULTS}"

clean:
	# With true we just let make know the command went OK.
	[ -d "${RESULTS}" ] && find "${RESULTS}" -delete || true
	[ -d "${INPUTS}" ] && find "${INPUTS}" -delete || true
	git checkout -- "${RESULTS}" "${INPUTS}"
