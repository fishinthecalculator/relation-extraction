define default-state-dir
  string-append
    getcwd
    . "/results"

process search-tokens (with state-dir)
  packages "python-wrapper" "python-rdflib"
  inputs
    . split: "inputs/split"
    . entities: : string-append state-dir "/entities"
    . vn: "inputs/uby"
  outputs uby-dir: : string-append state-dir "/uby-neighbors"
  # bash {
    python bin/search_tokens.py -e {{inputs:entities}}/db/tweets_and_entities.tsv -s {{inputs:split}} -u {{inputs:vn}} -o {{outputs:uby-dir}}
  }

workflow UBY
  processes
    search-tokens default-state-dir
