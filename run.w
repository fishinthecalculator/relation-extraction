define dbpedia-workflow
  load-workflow "workflows/dbpedia.w"

define uby-workflow
  load-workflow "workflows/uby.w"

define fim-workflow
  load-workflow "workflows/fim.w"

workflow main
  processes
    apply
      . auto-connect
      append
        workflow-processes dbpedia-workflow
        workflow-processes uby-workflow
        workflow-processes fim-workflow
