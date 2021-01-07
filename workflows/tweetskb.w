define default-state-dir
  string-append
    getcwd
    . "/results"

process tweetskb-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . tweetskb: "inputs/tweetskb"
    . tweets: : string-append state-dir "/tweets"
  outputs tweetskb-dir: : string-append state-dir "/tweetskb"
  # bash {
    python bin/fe_tweetskb.py -t {{inputs:tweetskb}} -i {{inputs:tweets}} -o {{outputs:tweetskb-dir}}
  }

workflow tweetskb
  processes
    tweetskb-feature-extraction default-state-dir
