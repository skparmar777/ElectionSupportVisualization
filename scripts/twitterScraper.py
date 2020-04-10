import csv
import re
import tweepy
import string
import pandas as pd
import os

from pymongo import MongoClient
from dotenv import load_dotenv

from sentiment import text_to_sentiment


def remove_control_chars(s):
    s1 = ''.join(filter(lambda x: x in string.printable, s))
    return re.sub(r'[^\w]', ' ', s1)


def build_connection_string():
    load_dotenv()
    return 'mongodb+srv://' + os.getenv('MONGO_USERNAME') + ':' + os.getenv(
        'MONGO_PASSWORD') + '@sohams2cluster-upcyf.mongodb.net/test?retryWrites=true&w=majority'


cities_df = pd.read_csv(r'census_data/cleaned_il_data.csv')


class Tweet:
    def __init__(self, id, date, lat, long, user_name, likes, party, candidate, text, sentiment, tokens, user_location):
        self.id = id
        self.date = date
        self.lat = lat
        self.long = long
        self.name = user_name
        self.likes = likes
        self.party = party
        self.candidate = candidate
        self.text = text
        self.sentiment = sentiment
        self.tokens = tokens
        self.user_location = user_location

    def format_csv_row(self):
        row = [self.id,
               self.date,
               self.candidate,
               self.party,
               self.name,
               self.user_location,
               self.text,
               self.sentiment,
               self.tokens,
               self.likes,
               self.lat,
               self.long]
        return row

    def format_json(self):
        doc = {'id': self.id, 'date': self.date, 'candidate': self.candidate, 'party': self.party, 'name': self.name,
               'location': self.user_location, 'text': self.text, 'sentiment': self.sentiment, 'tokens': self.tokens,
               'likes': self.likes, 'lat': self.lat, 'long': self.long}
        return doc


# consumer_key = "YnnVhRE07letJqq5lwAjzhkkW"
# consumer_secret = "CdqLlC1ALQHsiTsyuKCR1ZDcLQfLDmtFttA2AMoWtqCmX8pLuT"
# access_token = "2879004436-4LKhCOuFYdPL4RTns26ZejiWc7si6aMf1LVX53j"
# access_token_secret = "4ArzANk8q8lyodhBJTwT7S7dHYY0vjQHc4hcgeaNFp6mq"

consumer_key = "SFcxwLBVF4YmVERD8YbFAbHVR"
consumer_secret = "bAjMKe6BeEIQ9lH3JzJsJsRTRjkHQg9hHRgEB42Xdbjqfxv6Fz"
access_token = "717755279488782336-w9RE9xptHI5rPFflQf4qy47ofqsJitO"
access_token_secret = "WgVxnf7ZaYPDqsPygjK6FCGwo9pw9w4nKdQeaoLAl6j85"

auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# process sanders tweets
tweet_csv = open('tweets_Test.csv', 'w', encoding='UTF-8', newline='')
tweet_csvWriter = csv.writer(tweet_csv)
tweet_csvWriter.writerow(
    ['tweet_id', 'date', 'candidate', 'party', 'user_name', 'user_location', 'text', 'sentiment', 'tokens', 'likes',
     'latitude', 'longitude'])
count = 0
client = MongoClient(build_connection_string())
db = client["election"]
collection = db["tweets"]

# use a radius that covers all of illinois, pull 100 most recent tweets
for tweet in tweepy.Cursor(api.search, q="bernie sanders", geocode='40.049174,-88.858617,193mi', count=10000).items(
        10000):
    tweet_txt = tweet.text
    name = tweet.user.name
    user_loc = ''
    lat = 0
    long = 0
    if 'bernie' not in tweet_txt.lower() and 'sanders' not in tweet_txt.lower():
        continue
    if tweet.place != None:
        full_location = tweet.place.full_name
        l = full_location.split()
        if "IL" in l[1]:
            res = cities_df[cities_df['city'] == tweet.place.name]
            lat = res.iloc[0]['lat']
            long = res.iloc[0]['lng']
            user_loc = tweet.place.name
            sentiment_tokens = text_to_sentiment(tweet_txt)
            if sentiment_tokens == "no valid words in text":
                continue
            tweet_obj = Tweet(tweet.id, tweet.created_at, lat, long, name, tweet.favorite_count, "Democrat", "Sanders",
                              tweet_txt, sentiment_tokens[0], sentiment_tokens[1], user_loc)
            print("writing row, bernie ")
            tweet_csvWriter.writerow(tweet_obj.format_csv_row())
            collection.insert_one(tweet_obj.format_json())


for tweet in tweepy.Cursor(api.search, q="joe biden", geocode='40.049174,-88.858617,193mi', count=10000).items(
        10000):
    tweet_txt = tweet.text
    name = tweet.user.name
    user_loc = ''
    lat = 0
    long = 0
    if 'joe' not in tweet_txt.lower() and 'biden' not in tweet_txt.lower():
        continue
    if tweet.place != None:
        full_location = tweet.place.full_name
        l = full_location.split()
        if "IL" in l[1]:
            res = cities_df[cities_df['city'] == tweet.place.name]
            lat = res.iloc[0]['lat']
            long = res.iloc[0]['lng']
            user_loc = tweet.place.name
            sentiment_tokens = text_to_sentiment(tweet_txt)
            if sentiment_tokens == "no valid words in text":
                continue
            tweet_obj = Tweet(tweet.id, tweet.created_at, lat, long, name, tweet.favorite_count, "Democrat", "Biden",
                          tweet_txt, sentiment_tokens[0], sentiment_tokens[1], user_loc)
            print("writing row, joe")
            tweet_csvWriter.writerow(tweet_obj.format_csv_row())
            collection.insert_one(tweet_obj.format_json())

for tweet in tweepy.Cursor(api.search, q="donald trump", geocode='40.049174,-88.858617,193mi', count=10000).items(
        10000):
    tweet_txt = tweet.text
    name = tweet.user.name
    user_loc = ''
    lat = 0
    long = 0
    if 'donald' not in tweet_txt.lower() and 'trump' not in tweet_txt.lower():
        continue
    if tweet.place != None:
        full_location = tweet.place.full_name
        l = full_location.split()
        if "IL" in l[1]:
            res = cities_df[cities_df['city'] == tweet.place.name]
            lat = res.iloc[0]['lat']
            long = res.iloc[0]['lng']
            user_loc = tweet.place.name
            sentiment_tokens = text_to_sentiment(tweet_txt)
            if sentiment_tokens == "no valid words in text":
                continue
            tweet_obj = Tweet(tweet.id, tweet.created_at, lat, long, name, tweet.favorite_count, "Republican", "Trump",
                          tweet_txt, sentiment_tokens[0], sentiment_tokens[1],user_loc)
            print("writing row, trump")
            tweet_csvWriter.writerow(tweet_obj.format_csv_row())
            collection.insert_one(tweet_obj.format_json())
