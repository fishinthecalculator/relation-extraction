define default-state-dir
  file
    getcwd
    . / "results"

process print-rules (with state-dir)
  packages "python-wrapper" "python-rdflib" "coreutils"
  inputs
    . fim-out: : file state-dir / "fim"
  outputs
    . rules: : file state-dir / "fim" / "rules.txt"
  # bash {
    python bin/print_rules.py -r `ls "{{outputs:fim-out}}/*.npz" | head -1`
  }

process run-show-graph (with state-dir)
  packages "raptor2" "graphviz" "sed" "parallel" "coreutils" "findutils"
  inputs
    . bags: : file state-dir / "features" / "bags"
  # bash {
    find {{inputs:bags}} -type f -name "*.ttl" | parallel "bin/show_graph.sh {} turtle"
  }


workflow utils
  processes
    auto-connect
      print-rules default-state-dir
      run-show-graph default-state-dir
