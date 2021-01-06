HERE=$(shell pwd)

TEST_DIR=${HERE}/test-inputs

TEST_UBY="${TEST_DIR}/uby"
TEST_TWEETSKB="${TEST_DIR}/tweetskb"
TEST_DBPEDIA="${TEST_DIR}/dbpedia"

GENERATED=run.svg inputs/uby inputs/split inputs/tweetskb inputs/dbpedia "${TEST_DIR}" results/entities/*.tsv results/entities/db/*.tsv results/related/*.ttl results/fim/*.pickle results/fim/*.npy results/fim/graphs/*.svg results/fim/*.txt results/fim/graphs/*.ttl results/uby-neighbors/*.ttl

FREE_INPUTS=--input=inputs/uby=datasets/vn.nt --input=inputs/split=./SPLIT_TOKEN --input=inputs/tweetskb=datasets/first_10M_lines.n3 --input=inputs/dbpedia=datasets/mappingbased_properties_cleaned_en.nt

N_LINES=5000

all: graph
	guix workflow -r run.w ${FREE_INPUTS}

dbpedia: graph
	guix workflow -r workflows/dbpedia.w ${FREE_INPUTS}

fim: graph
	guix workflow -r workflows/fim.w ${FREE_INPUTS}

test: graph
	mkdir -p "${TEST_DIR}"

	head -n ${N_LINES} datasets/vn.nt > ${TEST_UBY}
	head -n ${N_LINES} datasets/first_10M_lines.n3 > ${TEST_TWEETSKB}
	head -n ${N_LINES}00 datasets/mappingbased_properties_cleaned_en.nt > ${TEST_DBPEDIA}

	guix workflow -r run.w --input=inputs/uby=${TEST_UBY} --input=inputs/split=./SPLIT_TOKEN --input=inputs/tweetskb=${TEST_TWEETSKB} --input=inputs/dbpedia=${TEST_DBPEDIA}

graph:
	guix workflow --graph=run.w | dot -Tsvg -o run.svg

compress:
	tar -cf archive/$(shell date +%Y-%m-%d+%H:%M).tar.bz2 --use-compress-prog=pbzip2 results/

clean:
	rm -rf ${GENERATED}
