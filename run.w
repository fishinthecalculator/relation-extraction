define project
  getcwd

define tweet-extraction
  string-append project "/tweet-extraction"

define tweets-and-entities.tsv
  string-append tweet-extraction "/tweets_and_entities.tsv"

define tweets-dir
  string-append tweet-extraction "/tweets"

define dbpedia
  string-append tweet-extraction "/mappingbased_properties_cleaned_en.nt"

define related
  string-append tweet-extraction "/related"

process select-tweets-entities
  packages "sed" "ripgrep"
  inputs "triples"
  outputs tweets-and-entities.tsv
  # bash {
    tweet-extraction/select-tweets-entities.sh {{inputs}} > {{outputs}}
  }

process tweets-with-multiple-entities
  packages "gawk" "coreutils" "ripgrep"
  inputs tweets-and-entities.tsv
  outputs tweets-dir
  # bash {
    tweet-extraction/tweets-with-multiple-entities.sh {{inputs}} {{outputs}}
  }

process tweets-with-dbpedia-relations
  packages "python-wrapper" "python-rdflib" "bash"
  inputs
    . tweets: tweets-dir
    . db: dbpedia
  outputs
    . rel: related
    . props: string-append tweet-extraction "/properties.csv"
  # bash {
    python tweet-extraction/extract-relations.py -t {{inputs:tweets}} -d {{inputs:db}} -o {{outputs:rel}} > {{outputs:props}}
  }


workflow thesis
  processes
    auto-connect
      . select-tweets-entities
      . tweets-with-multiple-entities
      . tweets-with-dbpedia-relations
