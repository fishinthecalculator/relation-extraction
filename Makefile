HERE=$(shell pwd)

ARCHIVE=${HERE}/archive
DATASETS=${HERE}/datasets
INPUTS=inputs
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

FREE_INPUTS=-i "${UBY}"="${UBY_DATA}" -i "${TWEETSKB}"="${TWEETSKB_DATA}" -i "${DBPEDIA}"="${DBPEDIA_DATA}"

all: graph
	guix workflow run run.w ${FREE_INPUTS}

graph:
	guix workflow graph run.w | dot -Tsvg -o run.svg

dbpedia: graph
	guix workflow run workflows/dbpedia.w ${FREE_INPUTS}

uby: graph
	guix workflow run workflows/uby.w ${FREE_INPUTS}

bags: graph
	guix workflow run workflows/merge.w ${FREE_INPUTS}

fim: graph
	guix workflow run workflows/fim.w ${FREE_INPUTS}

test: graph
	mkdir -p "${INPUTS}"

	head -n ${N_LINES} "${TWEETSKB_DATA}" > "${TWEETSKB}"
	head -n ${N_LINES} "${DBPEDIA_DATA}" > "${DBPEDIA}"

	guix workflow run run.w ${FREE_INPUTS}

scrape:
	tweet_text.py -i "${RESULTS}/tweets" -o "${RESULTS}/tweets"

compress:
	tar -cf "${ARCHIVE}"/$(shell date +%Y-%m-%d+%H.%M)-$(shell git log | head -1 | cut -d " " -f 2).tar.bz2 --use-compress-prog=pbzip2 "${RESULTS}"

clean:
	# With true we just let make know the command went OK.
	[ -d "${RESULTS}" ] && find "${RESULTS}" -delete || true
	[ -d "${INPUTS}" ] && find "${INPUTS}" -delete || true
	git checkout -- "${RESULTS}" "${INPUTS}"
