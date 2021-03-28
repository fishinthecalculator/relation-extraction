define default-state-dir
  file
    getcwd
    . / "results"

process uby-feature-extraction (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . split: "inputs/split"
    . entities: : file state-dir / "entities"
    . ids: : file state-dir / "tweets" / "ids.tsv"
    . vn: "inputs/uby"
  outputs uby-f: : file state-dir / "features" / "verbnet"
  # bash {
    python bin/feature_extraction.py -s uby -t {{inputs:entities}} -i {{inputs:ids}} -f {{inputs:split}} -u {{inputs:vn}} -o {{outputs:uby-f}}
  }

workflow UBY
  processes
    uby-feature-extraction default-state-dir
