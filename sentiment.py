import os
import tweepy

from elasticsearch import Elasticsearch
from textblob import TextBlob

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

# Index tweets in Elasticsearch

es = Elasticsearch()
index_name = 'tweets'

def index_tweet(tweet, search_phrase):
    tweet['search_phrase'] = search_phrase
    es.create(index=index_name,
              doc_type='tweet',
              id=tweet['id'],
              body=tweet
              )

def pull_1500_tweets(search_phrase):
    for i in range(0, 15):
        if i == 0:
            results = api.search(q=search_phrase, count=100, result_type='recent')
        else:
            results = api.search(q=search_phrase, count=100, result_type='recent', max_id=next_max_id)
        next_max_id = results.next_results.split('max_id=')[1].split('&')[0]
        for tweet in results:
            index_tweet(tweet._json, search_phrase)

pull_1500_tweets('search term here')

# Run analysis on them with TextBlob

search = es.search(doc_type='tweet', size=1500, q='search_phrase:"search term here"')
len(search['hits']['hits'])

total_polarity = 0
for tweet in search['hits']['hits']:
    tweet_blob = TextBlob(tweet['_source']['text'])
    total_polarity += tweet_blob.sentiment.polarity
average_sentiment = total_polarity / 1500
print average_sentiment