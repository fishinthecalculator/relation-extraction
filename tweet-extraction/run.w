define project
  string-append
    getenv "HOME"
    . "/code/Thesis"

define tweet-extraction
  string-append project "/tweet-extraction"

define tweets-and-entities
  string-append tweet-extraction "/tweets_and_entities"

define tweets-dir
  string-append tweets-and-entities "/tweets"

define related
  string-append tweet-extraction "/related"

process select-tweets-entities
  packages "sed" "ripgrep" "parallel" "coreutils"
  inputs "triples"
  outputs tweets: tweets-and-entities
  # bash {
    tweet-extraction/select-tweets-entities.sh {{inputs}} {{outputs:tweets}}
  }

process tweets-with-dbpedia-relations
  packages "python-wrapper" "python-rdflib"
  inputs
    . tweets: tweets-dir
    . db: "dbpedia"
  outputs
    . rel: related
  # bash {
    python tweet-extraction/extract-relations.py -t {{inputs:tweets}} -d {{inputs:db}} -o {{outputs:rel}}
  }


workflow thesis
  processes
    auto-connect
      . select-tweets-entities
      . tweets-with-dbpedia-relations
