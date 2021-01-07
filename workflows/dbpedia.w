define default-state-dir
  string-append
    getcwd
    . "/results"

process dbpedia-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . entities: : string-append state-dir "/entities"
    . tweets: : string-append state-dir "/tweets"
    . db: "inputs/dbpedia"
  outputs
    . rel: : string-append state-dir "/related"
  # bash {
    python bin/fe_dbpedia.py -i {{inputs:tweets}} -t {{inputs:entities}} -d {{inputs:db}} -o {{outputs:rel}}
  }


workflow dbpedia
  processes
    dbpedia-feature-extraction default-state-dir
