define default-state-dir
  string-append
    getcwd
    . "/results"

process run-fim (with state-dir)
  packages "python-wrapper" "python-rdflib" "python-numpy"
  inputs
    . uby-dir: : string-append state-dir "/uby-neighbors"
    . rel: : string-append state-dir "/related"
    . tweetskb: "inputs/tweetskb"
  outputs
    . fim-out: : string-append state-dir "/fim"
  # bash {
    python bin/fim.py -t {{inputs:tr}} -u {{inputs:uby-dir}} -r {{inputs:rel}} -o {{outputs:fim-out}}\

    python bin/print_rules.py -c {{outputs:fim-out}}/columns.npy -r {{outputs:fim-out}}/rules.pickle -s cosine > {{outputs:fim-out}}/rules_cosine.txt
    python bin/print_rules.py -c {{outputs:fim-out}}/columns.npy -r {{outputs:fim-out}}/rules.pickle -s maxconf > {{outputs:fim-out}}/rules_maxconf.txt
    python bin/print_rules.py -c {{outputs:fim-out}}/columns.npy -r {{outputs:fim-out}}/rules.pickle -s lift > {{outputs:fim-out}}/rules_lift.txt
    python bin/print_rules.py -c {{outputs:fim-out}}/columns.npy -r {{outputs:fim-out}}/rules.pickle -s kulc > {{outputs:fim-out}}/rules_kulc.txt
    python bin/print_rules.py -c {{outputs:fim-out}}/columns.npy -r {{outputs:fim-out}}/rules.pickle -s allconf > {{outputs:fim-out}}/rules_allconf.txt
    python bin/print_rules.py -c {{outputs:fim-out}}/columns.npy -r {{outputs:fim-out}}/rules.pickle -s coherence > {{outputs:fim-out}}/rules_coherence.txt

  }

process run-show-graph (with state-dir)
  packages "raptor2" "graphviz" "sed" "parallel" "coreutils"
  inputs
    . fim-out: : string-append state-dir "/fim"
  # bash {
    parallel "bin/show-graph.sh {} turtle" ::: {{inputs:fim-out}}/graphs/*.ttl
  }

workflow frequent-itemset-mining
  processes
    auto-connect
      run-fim default-state-dir
      run-show-graph default-state-dir
