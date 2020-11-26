define project
  string-append
    getenv "HOME"
    . "/code/Thesis"

define uby
  string-append project "/UBY"

define neighbors-dir
  string-append uby "/neighbors"

define tweet-extraction
  string-append project "/tweet-extraction"

define tweets-and-entities.tsv "/tmp/tweets_and_entities.tsv"

process search-tokens
  packages "python-wrapper" "python-rdflib"
  inputs
    . split: "split"
    . tae: tweets-and-entities.tsv
    . vn: "uby"
  outputs ttl-dir: neighbors-dir
  # bash {
    python UBY/search-tokens.py -e {{inputs:tae}} -s {{inputs:split}} -u {{inputs:vn}} -o {{outputs:ttl-dir}}
  }

workflow thesis
  processes search-tokens
