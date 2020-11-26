define project
  string-append
    getenv "HOME"
    . "/code/Thesis"

define tweet-extraction
  string-append project "/tweet-extraction"

define tweets-and-entities.tsv "/tmp/tweets_and_entities.tsv"

define tweets-dir
  string-append tweet-extraction "/tweets"

define properties.csv "/tmp/properties.csv"

define related
  string-append tweet-extraction "/related"

process select-tweets-entities
  packages "sed" "ripgrep"
  inputs "triples"
  outputs tae: tweets-and-entities.tsv
  # bash {
    tweet-extraction/select-tweets-entities.sh {{inputs}} > {{outputs:tae}}
  }

process tweets-with-multiple-entities
  packages "coreutils" "ripgrep"
  inputs tae: tweets-and-entities.tsv
  outputs tweets: tweets-dir
  # bash {
    tweet-extraction/tweets-with-multiple-entities.sh {{inputs:tae}} {{outputs:tweets}}
  }

process tweets-with-dbpedia-relations
  packages "python-wrapper" "python-rdflib"
  inputs
    . tweets: tweets-dir
    . db: "dbpedia"
  outputs
    . rel: related
    . props: properties.csv
  # bash {
    python tweet-extraction/extract-relations.py -t {{inputs:tweets}} -d {{inputs:db}} -o {{outputs:rel}} > {{outputs:props}}
  }


workflow thesis
  processes
    auto-connect
      . select-tweets-entities
      . tweets-with-multiple-entities
      . tweets-with-dbpedia-relations
