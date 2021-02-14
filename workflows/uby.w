define default-state-dir
  file
    getcwd
    . / "results"

process uby-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . split: "inputs/split"
    . entities: : file state-dir / "entities"
    . tweets: : file state-dir / "tweets"
    . vn: "inputs/uby"
  outputs uby-dir: : file state-dir / "uby-neighbors"
  # bash {
    python bin/feature_extraction.py -s uby -t {{inputs:entities}} -i {{inputs:tweets}} -f {{inputs:split}} -u {{inputs:vn}} -o {{outputs:uby-dir}}
  }

workflow UBY
  processes
    uby-feature-extraction default-state-dir
