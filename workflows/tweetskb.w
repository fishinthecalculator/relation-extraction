define default-state-dir
  file
    getcwd
    . / "results"

process tweetskb-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . tweetskb: "inputs/tweetskb"
    . tweets: : file state-dir / "tweets"
  outputs tweetskb-dir: : file state-dir / "tweetskb"
  # bash {
    python bin/fe_tweetskb.py -t {{inputs:tweetskb}} -i {{inputs:tweets}} -o {{outputs:tweetskb-dir}}
  }

workflow tweetskb
  processes
    tweetskb-feature-extraction default-state-dir
