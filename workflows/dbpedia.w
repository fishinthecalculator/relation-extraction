define default-state-dir
  string-append
    getcwd
    . "/results"

process select-tweets-entities (with state-dir)
  packages "sed" "ripgrep" "parallel" "coreutils"
  inputs tweetskb: "inputs/tweetskb"
  outputs
    . entities: : string-append state-dir "/entities"
  # bash {
    bin/select_tweets_entities.sh {{inputs:tweetskb}} {{outputs:entities}}
    cat results/entities/db/ids.tsv | sort -u > results/entities/db/unique_ids.tsv
  }

process dbpedia-relationships (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . entities: : string-append state-dir "/entities"
    . db: "inputs/dbpedia"
  outputs
    . rel: : string-append state-dir "/related"
  # bash {
    python bin/extract_relations.py -t {{inputs:entities}} -d {{inputs:db}} -o {{outputs:rel}}
  }


workflow dbpedia
  processes
    auto-connect
      select-tweets-entities default-state-dir
      dbpedia-relationships default-state-dir
