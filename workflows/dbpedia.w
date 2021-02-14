define default-state-dir
  file
    getcwd
    . / "results"

process dbpedia-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . entities: : file state-dir / "entities"
    . tweets: : file state-dir / "tweets"
    . db: "inputs/dbpedia"
  outputs
    . rel: : file state-dir / "related"
  # bash {
    python bin/feature-extraction.py -s dbpedia -i {{inputs:tweets}} -t {{inputs:entities}} -d {{inputs:db}} -o {{outputs:rel}}
  }


workflow dbpedia
  processes
    dbpedia-feature-extraction default-state-dir
