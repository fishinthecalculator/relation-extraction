define tweet-extraction-workflow
  load-workflow "tweet-extraction/run.w"

define uby-workflow
  load-workflow "UBY/run.w"

define fim-workflow
  load-workflow "fim/run.w"

workflow main
  processes
    apply
      . auto-connect
      append
        workflow-processes tweet-extraction-workflow
        workflow-processes uby-workflow
        workflow-processes fim-workflow
