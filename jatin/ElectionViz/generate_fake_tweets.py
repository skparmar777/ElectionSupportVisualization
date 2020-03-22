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

FAKE_FIRST_NAMES = [
    'Jatin',
    'Sejal',
    'Soham',
    'Don',
    'Adam',
    'Sara',
    'Madeline'
]

FAKE_LAST_NAMES = [
    'Smith',
    'Anderson',
    'Jollyrancher',
    'Goldstein',
    'Halloway'
]

CUR_TIME = datetime.now(pytz.utc) # all times in UTC
DAY_RANGE = 90 # can generate times between now and DAY_RANGE days ago
START_TIME = CUR_TIME - timedelta(days=DAY_RANGE)

NUM_DISTRICTS = 18


# ----------------------------

def select_random(l):
    return l[random.randint(0, len(l) - 1)]

def generate_random_tweet():
    # same format as create_sql_query
    tweet, candidate, party = select_random(FAKE_TWEETS)
    first = select_random(FAKE_FIRST_NAMES)
    last = select_random(FAKE_LAST_NAMES)
    district = random.randint(1, 18)

    delta = CUR_TIME - START_TIME
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    tweet_date = START_TIME + timedelta(seconds=random_second)

    likes = int(random.gauss(50, 100))
    while (likes < 0):
        likes = int(random.gauss(50, 100))

    return [tweet_date, district, first, last, likes, party, candidate, tweet]

def format_string(string):
    return "'" + string + "'"

def generate_and_push_tweets(num_fake_tweets):
    '''
    format:
    tweet_date DATETIME ('YYYY-MM-DD HH:MM:SS'),
    district INT,
    first_name CHAR(100),
    last_name CHAR(100),
    likes INT,
    party CHAR(100),
    candidate CHAR(100),
    tweet_text CHAR(560)
    '''
    for _ in range(num_fake_tweets):
        nt = generate_random_tweet()
        Tweets(tweet_date = nt[0],
                district = nt[1],
                first_name = nt[2],
                last_name = nt[3],
                likes = nt[4],
                party = nt[5],
                candidate = nt[6],
                tweet_text = nt[7]).save()
