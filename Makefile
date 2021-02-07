HERE=$(shell pwd)

TEST_DIR=${HERE}/inputs

TEST_UBY="${TEST_DIR}/uby"
TEST_TWEETSKB="${TEST_DIR}/tweetskb"
TEST_DBPEDIA="${TEST_DIR}/dbpedia"

FREE_INPUTS=-i inputs/uby=datasets/vn.nt -i inputs/split=./SPLIT_TOKEN -i inputs/tweetskb=datasets/first_10M_lines.n3 -i inputs/dbpedia=datasets/mappingbased_properties_cleaned_en.nt

N_LINES=500000

all: graph
	guix workflow run run.w ${FREE_INPUTS}

dbpedia: graph
	guix workflow run workflows/dbpedia.w ${FREE_INPUTS}

uby: graph
	guix workflow run workflows/uby.w ${FREE_INPUTS}

fim: graph
	guix workflow run workflows/fim.w ${FREE_INPUTS}

test: graph
	mkdir -p "${TEST_DIR}"

	head -n ${N_LINES} datasets/vn.nt > ${TEST_UBY}
	head -n ${N_LINES} datasets/first_10M_lines.n3 > ${TEST_TWEETSKB}
	head -n ${N_LINES} datasets/mappingbased_properties_cleaned_en.nt > ${TEST_DBPEDIA}

	guix workflow run run.w ${FREE_INPUTS}

graph:
	guix workflow graph run.w | dot -Tsvg -o run.svg

compress:
	tar -cf archive/$(shell date +%Y-%m-%d+%H.%M)-$(shell git log | head -1 | cut -d " " -f 2).tar.bz2 --use-compress-prog=pbzip2 results/

scrape:
	python bin/tweet_text.py -i results/tweets -o results/tweets

clean:
	rm -rf results "${TEST_DIR}"/*
	git checkout -- results inputs
