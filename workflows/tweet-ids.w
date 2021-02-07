define default-state-dir
  file
    getcwd
    . / "results"

process select-tweets-entities (with state-dir)
  packages "sed" "ripgrep" "parallel" "coreutils"
  inputs tweetskb: "inputs/tweetskb"
  outputs
    . entities: : file state-dir / "entities"
    . tweets: : file state-dir / "tweets"
  # bash {
    bin/select_tweets_entities.sh {{inputs:tweetskb}} {{state-dir}}
  }

workflow tweet-ids
  processes
    select-tweets-entities default-state-dir
