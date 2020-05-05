from tweets.models import Tweets
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime
import pytz

df_geo = gpd.read_file('data/illinois.json')

def lat_lon_to_district(lat, lon):
    p = Point(float(lon), float(lat))
    for i, r in df_geo.iterrows():
        if r['geometry'].contains(p):
            return r.DISTRICT
    else:
        print(f"ERROR COULD NOT MATCH {lat}, {lon}")
        exit(1)

for path in ['data/tweets_full_04_26_2020.csv', 'data/tweets_full_04_22_2020.csv', 'data/tweets_full_04_30_2020.csv', 'data/tweets_full_05_04_2020.csv', '../data/tweets_full.csv']:
    df = pd.read_csv(path)

    for i, r in df.iterrows():
        district = lat_lon_to_district(r.latitude, r.longitude)
        date = datetime.strptime(r.date, '%Y-%m-%d %H:%M:%S') # 2020-04-07 23:14:43
        date = pytz.utc.localize(date)
        Tweets(
            tweet_date = date,
            party = r['party'],
            candidate = r['candidate'],
            district = district,
            username = r['user_name'],
            likes = r['likes'],
            tweet_text = r['text'],
            sentiment = float(r['sentiment']),
            polarity = 'P' if float(r['sentiment']) >= 0 else 'N',
        ).save()
