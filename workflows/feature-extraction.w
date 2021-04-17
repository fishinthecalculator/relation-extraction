define src-dir
  getcwd

define default-inputs-dir
  file src-dir / "inputs"

define default-state-dir
  file src-dir / "results"

process select-tweets-entities (with inputs-dir state-dir)
  packages "sed" "ripgrep" "parallel" "coreutils"
  inputs tweetskb: : file inputs-dir / "tweetskb"
  outputs
    . entities: : file state-dir / "entities"
    . ids: : file state-dir / "tweets" / "ids.tsv"
  # bash {
    bin/select_tweets_entities.sh {{inputs:tweetskb}} {{state-dir}}
  }

process dbpedia-feature-extraction (with inputs-dir state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . entities: : file state-dir / "entities"
    . ids: : file state-dir / "tweets" / "ids.tsv"
    . db: : file inputs-dir / "dbpedia"
  outputs
    . dbpedia-f: : file state-dir / "features"
  # bash {
    python bin/feature_extraction.py -s dbpedia -i {{inputs:ids}} -n 3 -t {{inputs:entities}} -d {{inputs:db}} -o {{outputs:dbpedia-f}}

  }
  
process uby-feature-extraction (with inputs-dir state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . split: : file inputs-dir / "split"
    . vn: : file inputs-dir / "uby"
    . entities: : file state-dir / "entities"
    . ids: : file state-dir / "tweets" / "ids.tsv"
  outputs uby-f: : file state-dir / "features"
  # bash {
    python bin/feature_extraction.py -s uby -t {{inputs:entities}} -i {{inputs:ids}} -f {{inputs:split}} -u {{inputs:vn}} -o {{outputs:uby-f}}
  }

process merge-feature-graphs (with state-dir)
  packages "coreutils" "python-wrapper" "python-rdflib"
  inputs
    . ids: : file state-dir / "tweets" / "ids.tsv"
    . features: : file state-dir / "features"
  outputs
    . bags: : file state-dir / "features"
  # bash {
    python bin/merge_graphs.py -i {{inputs:ids}} -o {{outputs:bags}}
  }

workflow feature-extraction
  processes
    select-tweets-entities default-inputs-dir default-state-dir
    dbpedia-feature-extraction default-inputs-dir default-state-dir
    uby-feature-extraction default-inputs-dir default-state-dir
    merge-feature-graphs default-state-dir
