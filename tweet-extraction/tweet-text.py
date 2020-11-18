from pathlib import Path

import tweepy


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def lookup_tweets(tweet_IDs, api):
    full_tweets = []
    try:
        for chunk in chunks(tweet_IDs, 100):
            full_tweets.extend(
                api.statuses_lookup(id_=chunk, tweet_mode="extended")
            )
        return full_tweets
    except tweepy.TweepError:
        print('Something went wrong, quitting...')

consumer_key = 'mZDgi15ZZCJTC4ZSBlCux4PGP'
consumer_secret = '0ObCvpXpvDfsNV8754mukHTrIhbTQ3ICBFK0ZEGA4DNKdheEdQ'
access_token = '1310308525659303937-YoZjUNvRahy6yYT0FhDuyOxSkUiu2l'
access_token_secret = 'DywNt3gSaAkEvPsKKmcWV8fdEE2TEtE7YiTvdEwUOOcnv'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)



tweets = [int(t.name.split(".")[0][1:]) for t in Path(Path.cwd(), "related").iterdir() ]

results = lookup_tweets(tweets, api)

for tweet in results:
    if tweet:
        print(tweet.id)
        print("|-----------------------------------|")
        print(tweet.full_text)
        print("|===================================|")
