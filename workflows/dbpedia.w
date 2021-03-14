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
    . rel: : file state-dir / "related"
  # bash {
    python bin/feature_extraction.py -s dbpedia -i {{inputs:ids}} -t {{inputs:entities}} -d {{inputs:db}} -o {{outputs:rel}}
  }


workflow dbpedia
  processes
    dbpedia-feature-extraction default-state-dir
