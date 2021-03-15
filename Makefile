HERE=$(shell pwd)

ARCHIVE=${HERE}/archive
DATASETS=${HERE}/datasets
INPUTS=${HERE}/inputs
RESULTS=${HERE}/results

UBY=${INPUTS}/uby
TWEETSKB=${INPUTS}/tweetskb
DBPEDIA=${INPUTS}/dbpedia
SPLIT=${INPUTS}/split

IDS_DIR=${RESULTS}/tweets
IDS_TSV=${IDS_DIR}/ids.tsv
ENTITIES=${RESULTS}/entities

FEATURES=${RESULTS}/features
DBPEDIA_FEATURES=${FEATURES}/dbpedia
VN_FEATURES=${FEATURES}/verbnet
BAGS=${FEATURES}/bags

FIM=${RESULTS}/fim

N_LINES=500000

all: fim

setup:
	link_inputs.sh "${DBPEDIA}" "${TWEETSKB}" "${UBY}"

entities: setup
	select_tweets_entities.sh "${TWEETSKB}" "${RESULTS}"

dbpedia: entities
	feature_extraction.py -s dbpedia -i "${IDS_TSV}" -t "${ENTITIES}" -d "${DBPEDIA}" -o "${DBPEDIA_FEATURES}"

uby: dbpedia
	feature_extraction.py -s uby -i "${IDS_TSV}" -t "${ENTITIES}" -u "${UBY}" -f "${SPLIT}" -o "${VN_FEATURES}"

bags: uby
	merge_graphs.py -i "${IDS_TSV}" -u "${VN_FEATURES}" -d "${DBPEDIA_FEATURES}" -o "${BAGS}"

fim: bags
	run_fim.py -g "${BAGS}" -o "${FIM}"
	print_rules.py -r `find "${FIM}" -name "*.npz" | head -1`

test:
	mkdir -p "${INPUTS}"

	head -n ${N_LINES} "${DATASETS}"/tweetskb > "${TWEETSKB}"
	head -n ${N_LINES} "${DATASETS}"/dbpedia > "${DBPEDIA}"

compress:
	tar -cf "${ARCHIVE}"/$(shell date +%Y-%m-%d+%H.%M)-$(shell git log | head -1 | cut -d " " -f 2).tar.bz2 --use-compress-prog=pbzip2 "${RESULTS}"

scrape:
	tweet_text.py -i "${IDS_DIR}" -o "${IDS_DIR}"

clean:
	find "${RESULTS}" -delete
	find "${INPUTS}" -delete
	git checkout -- "${RESULTS}" "${INPUTS}"
