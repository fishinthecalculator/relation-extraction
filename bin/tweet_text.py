import os
import sys
import time

import tweepy

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_parser, make_logger, process_stdin_or_file
from relext.tweet.db import setup_db, tear_down
from relext.tweet.model import Tweet
from relext.tweet.twitter import consumer_key, consumer_secret, access_token, access_token_secret

logger = make_logger("tweet_text")


def is_visited(session, tweet_id):
    if not type(tweet_id) == int:
        tweet_id = int(tweet_id)
    # Check if tweet exists
    tweet = (
        session.query(Tweet)
            .filter(Tweet.tweet_id == tweet_id)
            .one_or_none()
    )

    # Does the tweet already exist?
    return tweet is not None


def chunks(session, lst, n):
    """Yield successive n-sized chunks from lst."""
    chunk = []
    for i, t in enumerate(lst):
        if len(chunk) == n:
            yield chunk
            chunk = []
        elif not is_visited(session, t):
            chunk.append(int(t.strip()))
    yield chunk


def lookup_tweets(chunk, api, attempt=0):
    if attempt < 5:
        try:
            return api.statuses_lookup(id_=chunk, tweet_mode="extended")
        except tweepy.TweepError:
            time.sleep(1)
            logger.warning(f"Something went wrong, retrying. Attempt {attempt + 1}...")
            lookup_tweets(chunk, api, attempt + 1)
    else:
        logger.error('Something went wrong, quitting...')
        return []


def store(session, tweet_dict):
    if not is_visited(session, tweet_dict["id"]):
        tweet_dict = Tweet(tweet_id=tweet_dict["id"],
                           full_text=tweet_dict["full_text"],
                           created_at=tweet_dict["created_at"],
                           lang=tweet_dict["lang"])
        try:
            session.add(tweet_dict)
            session.commit()
            return 1
        except:
            tear_down(session)
            raise
    return 0


def main(args):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    engine, session = setup_db(args.out_dir)

    def scrape(tweets):

        processed = 0
        total = 0
        try:
            for chunk in chunks(session, tweets, 150):
                if chunk is None:
                    break
                elif len(chunk) == 0:
                    continue
                logger.info(f"Trying to scrape {len(chunk)} tweets")
                logger.info(f"{total} where already tried")
                logger.info(f"{processed} where stored")
                results = lookup_tweets(chunk, api)
                if results:
                    for tweet in results:
                        total += 1
                        if tweet:
                            done = store(session, tweet._json)
                            processed += done
        except KeyboardInterrupt:
            logger.info("Catched keyboard interrupt, safely shutting down...")

    process_stdin_or_file(args, scrape)
    tear_down(session)
    sys.exit(0)


if __name__ == "__main__":
    parser = make_parser("tweet-text")
    args = parser.parse_args()

    main(args)
