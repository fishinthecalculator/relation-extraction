define default-state-dir
  file
    getcwd
    . / "results"

process print-rules (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . fim-out: : file state-dir / "fim"
  outputs
    . rules: : file state-dir / "fim" / "rules.txt"
  # bash {
    python bin/print_rules.py -r {{outputs:fim-out}}/rules.npz
  }

process run-show-graph (with state-dir)
  packages "raptor2" "graphviz" "sed" "parallel" "coreutils" "findutils"
  inputs
    . graphs: : file state-dir / "graphs"
  # bash {
    find {{inputs:graphs}} -type f -name "*.ttl" | parallel "bin/show_graph.sh {} turtle"
  }


workflow utils
  processes
    auto-connect
      print-rules default-state-dir
      run-show-graph default-state-dir
