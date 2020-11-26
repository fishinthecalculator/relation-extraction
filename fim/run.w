define project
  string-append
    getenv "HOME"
    . "/code/Thesis"

define fim
  string-append project "/fim"

define tweet-extraction
  string-append project "/tweet-extraction"

define related
  string-append tweet-extraction "/related"

define uby
  string-append project "/UBY"

define neighbors-dir
  string-append uby "/neighbors"

process run-fim
  packages "python-wrapper" "python-rdflib" "python-numpy" "bash"
  inputs
    . ttl-dir: neighbors-dir
    . rel: related
    . tr: "triples"
  outputs
    string-append fim "/out"
  # bash {
    python fim/fim.py -t {{inputs:tr}} -u {{inputs:ttl-dir}} -r {{inputs:rel}} -o {{outputs}}
  }


workflow thesis
  processes run-fim
