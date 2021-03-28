define default-state-dir
  file
    getcwd
    . / "results"


process merge-feature-graphs (with state-dir)
  packages "coreutils" "python-wrapper" "python-rdflib"
  inputs
    . ids: : file state-dir / "tweets" / "ids.tsv"
    . uby-f: : file state-dir / "features" / "verbnet"
    . dbpedia-f: : file state-dir / "features" / "dbpedia"
  outputs
    . bags: : file state-dir / "features" / "bags"
  # bash {
    python bin/merge_graphs.py -i {{inputs:ids}} -u {{inputs:uby-f}} -d {{inputs:dbpedia-f}} -o {{outputs:bags}}
  }

workflow merge-feature-graphs
  processes
    auto-connect
      merge-feature-graphs default-state-dir
