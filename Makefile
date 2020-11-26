TEST_UBY="uby"
TEST_TRIPLES="triples"
TEST_DBPEDIA="dbpedia"

N_LINES=1000

all:
	guix workflow -r run.w --input=uby=UBY/vn.nt --input=split=./SPLIT_TOKEN --input=triples=tweet-extraction/first_10M_lines.n3 --input=dbpedia=tweet-extraction/mappingbased_properties_cleaned_en.nt

test:
	[[ -f ${TEST_UBY} ]] || head -n ${N_LINES} UBY/vn.nt > ${TEST_UBY}
	[[ -f ${TEST_TRIPLES} ]] || head -n ${N_LINES} tweet-extraction/first_10M_lines.n3 > ${TEST_TRIPLES}
	[[ -f ${TEST_DBPEDIA} ]] ||  head -n ${N_LINES} tweet-extraction/mappingbased_properties_cleaned_en.nt > ${TEST_DBPEDIA}
	guix workflow -r run.w --input=uby=${TEST_UBY} --input=split=./SPLIT_TOKEN --input=triples=${TEST_TRIPLES} --input=dbpedia=${TEST_DBPEDIA}
