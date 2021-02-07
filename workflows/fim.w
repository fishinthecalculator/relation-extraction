import
  guix packages
  guix licenses
  guix download
  guix build-system python
  guix utils

define default-state-dir
  file
    getcwd
    . / "results"

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

process merge-feature-graphs (with state-dir)
  packages "guile" "guile-config" "guile-rdf" "guix"
  inputs
    . tweets: : file state-dir / "tweets"
    . uby-dir: : file state-dir / "uby-neighbors"
    . rel: : file state-dir / "related"
    . tweetskb-dir: : file state-dir / "tweetskb"
  values:
    . ids:
    file
      first inputs
      . / "ids.tsv"
  outputs
    . graphs: : file state-dir / "graphs"
  # bash {
    guile -e main -s bin/merge-graphs -t {{inputs:tweetskb-dir}} -i {{values:ids}} -u {{inputs:uby-dir}} -d {{inputs:rel}} -o {{outputs:graphs}}
  }

process run-fim (with state-dir)
  packages "python-wrapper" "python-numpy" python-pyfim
  inputs
    . graphs: : file state-dir / "graphs"
  outputs
    . fim-out: : file state-dir / "fim"
  # bash {
    python bin/run_fim.py -i {{inputs:tweets}} -g {{inputs:graphs}} -o {{outputs:fim-out}}

    python bin/print_rules.py -r {{outputs:fim-out}}/rules.npz
  }

process run-show-graph (with state-dir)
  packages "raptor2" "graphviz" "sed" "parallel" "coreutils" "findutils"
  inputs
    . graphs: : file state-dir / "fim"
  # bash {
    find {{inputs:fim-out}} -type f -name "*.ttl" | parallel "bin/show_graph.sh {} turtle"
  }

workflow frequent-itemset-mining
  processes
    auto-connect
      merge-graphs default-state-dir
      run-fim default-state-dir
      run-show-graph default-state-dir
