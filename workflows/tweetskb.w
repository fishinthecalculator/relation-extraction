define src-dir
  getcwd

define default-inputs-dir
  file src-dir / "inputs"

define default-state-dir
  file src-dir / "results"

process tweetskb-feature-extraction (with inputs-dir state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . tweetskb: : file inputs-dir / "tweetskb"
    . ids: : file state-dir / "tweets" / "ids.tsv"
  outputs tweetskb-dir: : file state-dir / "tweetskb"
  # bash {
    python bin/feature_extraction.py -s tweetskb -t {{inputs:tweetskb}} -i {{inputs:ids}} -o {{outputs:tweetskb-dir}}
  }

workflow tweetskb
  processes
    tweetskb-feature-extraction default-inputs-dir default-state-dir
