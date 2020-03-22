from django.shortcuts import render
from django.db.models import Sum, Max, Count
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from datetime import timezone
import json

from .models import Tweets

import pprint

BASE_QUERY = "SELECT tweets.tweet_id, tweets.district, tweets.party, T1.total_likes, T1.num_tweets, tweets.first_name, tweets.last_name, T1.max_likes, tweets.tweet_text, tweets.tweet_date \
            FROM \
                (SELECT tweets.district as district, tweets.party as party, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                FROM tweets \
                GROUP BY tweets.district, tweets.party) T1, tweets \
            WHERE tweets.district = T1.district \
            AND tweets.party = T1.party \
            AND tweets.likes = T1.max_likes"

def serialize_results(res):
    data = []
    for i in range(len(res)):
        new = {}
        new['district'] = res[i].district
        new['party'] = res[i].party.strip()
        new['total_likes'] = res[i].total_likes
        new['num_tweets'] = res[i].num_tweets
        new['max_likes'] = res[i].max_likes
        new['tweet_text'] = res[i].tweet_text.strip()
        new['first_name'] = res[i].first_name.strip()
        new['last_name'] = res[i].last_name.strip()
        dt = res[i].tweet_date
        new['tweet_date'] = dt.strftime('%B %d at %H:%M') # ex: March 21 at 18:13
        data.append(new)
    return data

# Create your views here.
@csrf_exempt
def tweet_view(request):
    # Django's ORM is good but I couldn't figure out how to get the query below using it
    # query1 = Tweets.objects.values('district', 'party').annotate(total_likes = Sum('likes'), num_tweets = Count('tweet_id'), max_likes = Max('likes'))

    # POST when daterange is queried
    if request.method == 'POST':
        # ex of request.body: daterange=March 5, 2017 - March 11, 2017
        daterange = request.body.decode('utf-8').split('=')[1]
        splits = daterange.split('-')
        start = splits[0].strip()
        stop = splits[1].strip()
        start = datetime.strptime(start, '%B %d, %Y')
        stop = datetime.strptime(stop, '%B %d, %Y') + timedelta(days=1)
        # adds time filter
        query = "SELECT tweets.tweet_id, tweets.district, tweets.party, T1.total_likes, T1.num_tweets, tweets.first_name, tweets.last_name, T1.max_likes, tweets.tweet_text, tweets.tweet_date \
                FROM \
                    (SELECT tweets.district as district, tweets.party as party, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                    FROM tweets \
                    WHERE tweets.tweet_date BETWEEN '{}' AND '{}'    \
                    GROUP BY tweets.district, tweets.party) T1, tweets \
                WHERE tweets.district = T1.district \
                AND tweets.party = T1.party \
                AND tweets.likes = T1.max_likes".format(start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'))
        # objs_tf = Tweets.objects.filter(tweet_date__range = [start, stop])
        res = list(Tweets.objects.raw(query))
        data = serialize_results(res)
        return HttpResponse(json.dumps(data))

    # get HTML and base map with everything in Tweets (1w)
    else:
        res = list(Tweets.objects.raw(BASE_QUERY))
        data = serialize_results(res)

        fp = open('tweets/data/illinois.json', 'rb')
        context = {
            'data': json.dumps(data),
            'map_json': json.dumps(json.load(fp))
        }
        fp.close()
        return render(request, 'templates/tweets_view.html', context)
