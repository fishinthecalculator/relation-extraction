define default-state-dir
  file
    getcwd
    . / "results"

process tweetskb-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . tweetskb: "inputs/tweetskb"
    . ids: : file state-dir / "tweets" / "ids.tsv"
  outputs tweetskb-dir: : file state-dir / "tweetskb"
  # bash {
    python bin/feature_extraction.py -s tweetskb -t {{inputs:tweetskb}} -i {{inputs:ids}} -o {{outputs:tweetskb-dir}}
  }

workflow tweetskb
  processes
    tweetskb-feature-extraction default-state-dir
