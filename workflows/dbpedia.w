define default-state-dir
  file
    getcwd
    . / "results"

process dbpedia-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . entities: : file state-dir / "entities"
    . ids: : file state-dir / "tweets" / "ids.tsv"
    . db: "inputs/dbpedia"
  outputs
    . dbpedia-f: : file state-dir / "features" / "dbpedia"
  # bash {
    python bin/feature_extraction.py -s dbpedia -i {{inputs:ids}} -n 3 -t {{inputs:entities}} -d {{inputs:db}} -o {{outputs:dbpedia-f}}

  }


workflow dbpedia
  processes
    dbpedia-feature-extraction default-state-dir
