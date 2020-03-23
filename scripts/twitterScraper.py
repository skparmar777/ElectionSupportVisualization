import csv
import re
import tweepy
import string


def remove_control_chars(s):
    s1 = ''.join(filter(lambda x: x in string.printable, s))
    return re.sub(r'[^\w]', ' ', s1)


class Tweet:
    def __init__(self, id, date, lat, long, user_name, likes, party, candidate, text, user_location):
        self.id = id
        self.date = date
        self.lat = lat
        self.long = long
        self.name = user_name
        self.likes = likes
        self.party = party
        self.candidate = candidate
        self.text = text
        self.user_location = user_location

    def format_csv_row(self):
        row = [self.id,
               self.date,
               self.candidate,
               self.party,
               self.name,
               self.user_location,
               self.text,
               self.likes,
               self.lat,
               self.long]
        return row


consumer_key = "SFcxwLBVF4YmVERD8YbFAbHVR"
consumer_secret = "bAjMKe6BeEIQ9lH3JzJsJsRTRjkHQg9hHRgEB42Xdbjqfxv6Fz"
access_token = "717755279488782336-w9RE9xptHI5rPFflQf4qy47ofqsJitO"
access_token_secret = "WgVxnf7ZaYPDqsPygjK6FCGwo9pw9w4nKdQeaoLAl6j85"

auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# process sanders tweets
tweet_csv = open('tweets.csv', 'w')
tweet_csvWriter = csv.writer(tweet_csv)
tweet_csvWriter.writerow(['tweet_id', 'date', 'candidate', 'party', 'user_name', 'user_location', 'text', 'likes', 'latitude', 'longitude'])

# use a radius that covers all of illinois, pull 100 most recent tweets
for tweet in tweepy.Cursor(api.search, q="bernie sanders", geocode='40.049174,-88.858617,193mi', count=1000).items(
        1000):
    tweet_txt = remove_control_chars(tweet.text.lower())
    name = remove_control_chars(tweet.user.name.lower())
    user_loc = remove_control_chars(tweet.user.location.lower())
    coords = True
    if 'bernie' not in tweet_txt and 'sanders' not in tweet_txt:
        continue
    if tweet.coordinates is None:
        coords = False
    elif tweet.coordinates['coordinates'] is None or tweet.coordinates['type'] is not 'Point':
        coords = False

    if not coords:
        tweet_obj = Tweet(tweet.id, tweet.created_at, None, None, name, tweet.favorite_count, "Democrat", "Sanders",
                          tweet_txt, user_loc)
    else:
        # print('lat', tweet.coordinates['coordinates'][1], 'long', tweet.coordinates['coordinates'][0])
        tweet_obj = Tweet(tweet.id, tweet.created_at, tweet.coordinates['coordinates'][1],
                          tweet.coordinates['coordinates'][0], name, tweet.favorite_count, "Democrat", "Sanders",
                          tweet_txt, user_loc)

    tweet_csvWriter.writerow(tweet_obj.format_csv_row())

for tweet in tweepy.Cursor(api.search, q="joe biden", geocode='40.049174,-88.858617,193mi', count=1000).items(1000):
    tweet_txt = remove_control_chars(tweet.text.lower())
    name = remove_control_chars(tweet.user.name.lower())
    user_loc = remove_control_chars(tweet.user.location.lower())

    coords = True
    if 'joe' not in tweet_txt and 'biden' not in tweet_txt:
        continue
    if tweet.coordinates is None:
        coords = False
    elif tweet.coordinates['coordinates'] is None or tweet.coordinates['type'] is not 'Point':
        coords = False


    if not coords:
        tweet_obj = Tweet(tweet.id, tweet.created_at, None, None, name, tweet.favorite_count, "Democrat", "Biden",
                          tweet_txt, user_loc)
    else:
        # print('lat', tweet.coordinates['coordinates'][1], 'long', tweet.coordinates['coordinates'][0])
        tweet_obj = Tweet(tweet.id, tweet.created_at, tweet.coordinates['coordinates'][1],
                          tweet.coordinates['coordinates'][0], name, tweet.favorite_count, "Democrat", "Biden",
                          tweet_txt, user_loc)

    tweet_csvWriter.writerow(tweet_obj.format_csv_row())

for tweet in tweepy.Cursor(api.search, q="donald trump", geocode='40.049174,-88.858617,193mi', count=1000).items(1000):
    tweet_txt = remove_control_chars(tweet.text.lower())
    name = remove_control_chars(tweet.user.name.lower())
    user_loc = remove_control_chars(tweet.user.location.lower())

    coords = True
    if 'donald' not in tweet_txt and 'trump' not in tweet_txt:
        continue
    if tweet.coordinates is None:
        coords = False
    elif tweet.coordinates['coordinates'] is None or tweet.coordinates['type'] is not 'Point':
        coords = False

    # def __init__(self, id, date, lat, long, name, likes, party, candidate, text, user_location):
    if not coords:
        tweet_obj = Tweet(tweet.id, tweet.created_at, None, None, name, tweet.favorite_count, "Republican", "Trump",
                          tweet_txt, user_loc)
    else:
        # print('lat', tweet.coordinates['coordinates'][1], 'long', tweet.coordinates['coordinates'][0])
        tweet_obj = Tweet(tweet.id, tweet.created_at, tweet.coordinates['coordinates'][1],
                          tweet.coordinates['coordinates'][0], name, tweet.favorite_count, "Republican", "Trump",
                          tweet_txt, user_loc)

    tweet_csvWriter.writerow(tweet_obj.format_csv_row())
