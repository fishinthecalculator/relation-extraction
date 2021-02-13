define dbpedia-workflow
  load-workflow "workflows/dbpedia.w"

define uby-workflow
  load-workflow "workflows/uby.w"

define tweet-ids-workflow
  load-workflow "workflows/tweet-ids.w"

define tweetskb-workflow
  load-workflow "workflows/tweetskb.w"

define fim-workflow
  load-workflow "workflows/fim.w"

define utils
  load-workflow "workflows/utils.w"

workflow main
  processes
    apply
      . auto-connect
      append
        workflow-processes dbpedia-workflow
        workflow-processes uby-workflow
        workflow-processes tweet-ids-workflow
        workflow-processes tweetskb-workflow
        workflow-processes fim-workflow
        workflow-processes utils
