import
  guix packages
  guix licenses
  guix download
  guix build-system python
  guix utils

define default-state-dir
  string-append
    getcwd
    . "/results"

define python-pyfim
  package
    name "python-pyfim"
    version "6.28"
    source
      origin
        method url-fetch
        uri : pypi-uri "pyfim" version
        sha256
          base32
            . "11ajsx9dswsczxh1xq9k2m5spyf2y8sm8krl5qjc45w3rbcrklbn"
    build-system python-build-system
    home-page "http://www.borgelt.net/pyfim.html"
    synopsis
      . "Frequent Item Set Mining and Association Rule Induction for Python"
    description
      . "PyFIM is an extension module that makes several frequent item set mining
implementations available as functions in Python 2.7.x & 3.8.x.  Currently
@url{https://borgelt.net/apriori.html, apriori}, @url{https://borgelt.net/eclat.html, eclat},
@url{https://borgelt.net/fpgrowth.html, fpgrowth}, @url{https://borgelt.net/sam.html, sam},
@url{https://borgelt.net/relim.html, relim}, @url{https://borgelt.net/carpenter.html, carpenter},
@url{https://borgelt.net/ista.html, ista}, @url{https://borgelt.net/accretion.html, accretion} and
@url{https://borgelt.net/apriori.html, apriacc} are available as functions, although the interfaces
do not offer all of the options of the command line program.  (Note that @code{lcm} is available as
an algorithm mode of @code{eclat}).  There is also a \"generic\" function @code{fim}, which is essentially
the same function as @code{fpgrowth}, only with a simplified interface (fewer options).

Finally, there is a function @code{arules} for generating association rules (simplified interface compared
to @code{apriori}, @code{eclat} and @code{fpgrowth}, which can also be used to generate association rules."
    license expat

process run-fim (with state-dir)
  packages "python-wrapper" "python-rdflib" "python-numpy" python-pyfim
  inputs
    . uby-dir: : string-append state-dir "/uby-neighbors"
    . rel: : string-append state-dir "/related"
    . tweets: : string-append state-dir "/tweets"
    . tweetskb-dir: : string-append state-dir "/tweetskb"
  outputs
    . fim-out: : string-append state-dir "/fim"
  # bash {
    python bin/run_fim.py -t {{inputs:tweetskb-dir}} -i {{inputs:tweets}} -u {{inputs:uby-dir}} -d {{inputs:rel}} -o {{outputs:fim-out}}

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
    parallel "bin/show_graph.sh {} turtle" ::: {{inputs:fim-out}}/graphs/*.ttl
  }

workflow frequent-itemset-mining
  processes
    auto-connect
      run-fim default-state-dir
      run-show-graph default-state-dir
