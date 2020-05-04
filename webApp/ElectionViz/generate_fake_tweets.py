from datetime import timedelta
from datetime import datetime
import pytz
import random

from tweets.models import Tweets

# ---- CONFIG variables ----

# FORMAT
# text, candidate, party
FAKE_TWEETS = [
    ('Trump is great', 'Trump', 'Republican'),
    ('Trump is awesome!!', 'Trump', 'Republican'),
    ('Go trump :)', 'Trump', 'Republican'),
    ('This new policy by Trump is great', 'Trump', 'Republican'),
    ('Trump is a legend', 'Trump', 'Republican'),

    ('Biden rocks', 'Biden', 'Democrat'),
    ('Biden has great policies', 'Biden', 'Democrat'),
    ('Biden seems super cool', 'Biden', 'Democrat'),

    ('Feel the bern!', 'Bernie', 'Democrat'),
    ('Bernie is the G!', 'Bernie', 'Democrat'),
]

FAKE_USERNAMES = [
    'justin_math_nerd',
    'sejal_hedge_fund_manager',
    'soham_does_ml',
    'noice',
    'yippeeXD999',
    'wuuut',
    'who.dat',
    'abduuu'
]

CUR_TIME = datetime.now(pytz.utc) # all times in UTC
DAY_RANGE = 90 # can generate times between now and DAY_RANGE days ago
START_TIME = CUR_TIME - timedelta(days=DAY_RANGE)

NUM_DISTRICTS = 102


# ----------------------------

def select_random(l):
    return l[random.randint(0, len(l) - 1)]

def generate_random_tweet():
    # same format as create_sql_query
    tweet, candidate, party = select_random(FAKE_TWEETS)
    username = select_random(FAKE_USERNAMES)
    district = random.randint(0, NUM_DISTRICTS - 1)

    delta = CUR_TIME - START_TIME
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    tweet_date = START_TIME + timedelta(seconds=random_second)

    likes = int(random.gauss(5, 5))
    while (likes < 0):
        likes = int(random.gauss(5, 5))

    sentiment = random.gauss(0.1, 0.1) # slight positive
    while sentiment > 1 or sentiment < -1:
        sentiment = random.gauss(0.1, 0.1)
    polarity = 'P' if sentiment >= 0 else 'N'

    return [tweet_date, party, candidate, district, username, likes, tweet, sentiment, polarity]

def format_string(string):
    return "'" + string + "'"

def generate_and_push_tweets(num_fake_tweets):
    '''
    format:
    tweet_date DATETIME ('YYYY-MM-DD HH:MM:SS'),
    party CHAR(100),
    candidate CHAR(100),
    district INT,
    username VARCHAR(256),
    likes INT,
    tweet_text CHAR(560),
    sentiment FLOAT
    '''
    for _ in range(num_fake_tweets):
        nt = generate_random_tweet()
        Tweets(tweet_date = nt[0],
                party = nt[1],
                candidate = nt[2],
                district = nt[3],
                username = nt[4],
                likes = nt[5],
                tweet_text = nt[6],
                sentiment = nt[7],
                polarity = nt[8],
                ).save()
