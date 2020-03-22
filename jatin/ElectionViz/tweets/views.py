from django.shortcuts import render
from django.db.models import Sum, Max, Count
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from datetime import timezone
import json

from .models import Tweets, TweetsArchive
import numpy as np

import pprint

BASE_QUERY = "SELECT DISTINCT tweets.tweet_id, tweets.district, tweets.party, tweets.candidate, T1.total_likes, T1.num_tweets, tweets.first_name, tweets.last_name, T1.max_likes, tweets.tweet_text, tweets.tweet_date \
            FROM \
                (SELECT tweets.district as district, tweets.party as party, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                FROM tweets \
                GROUP BY tweets.district, tweets.party) T1, tweets \
            WHERE tweets.district = T1.district \
            AND tweets.party = T1.party \
            AND tweets.likes = T1.max_likes"

NUM_DISTRICTS = 18

def is_in_current_week(start, end):
    now = datetime.utcnow()
    last_monday = now + timedelta(days=-now.weekday(), hours=-now.hour, minutes=-now.minute, seconds=-now.second, microseconds=-now.microsecond)
    return start >= last_monday

def is_before_current_week(start, end):
    now = datetime.utcnow()
    last_monday = now + timedelta(days=-now.weekday(), hours=-now.hour, minutes=-now.minute, seconds=-now.second, microseconds=-now.microsecond)
    return end <= last_monday

def serialize_results(res, descriptor):
    '''
    res: queryset from Tweets or TweetsArchive
    descriptor: whether date is 'exact' or 'weekly'

    Format: DISTRICT->PARTY->CANDIDATE->[total_likes, num_tweets, max_likes, tweet_text, first_name, last_name]
    Also, each DISTRICT->PARTY gets a 'combined' category for cross-party comparisons
    '''
    parties = ['Democrat', 'Republican']
    data = {}
    for d in range(1, NUM_DISTRICTS + 1):
        data[d] = {}
        for party in parties:
            data[d][party] = {}

    for i in range(len(res)):
        district, party, candidate = res[i].district, res[i].party.strip(), res[i].candidate.strip()
        data[district][party][candidate] = {}
        cur = data[district][party][candidate]
        cur['total_likes'] = res[i].total_likes
        cur['num_tweets'] = res[i].num_tweets
        cur['max_likes'] = res[i].max_likes
        cur['tweet_text'] = res[i].tweet_text.strip()
        cur['first_name'] = res[i].first_name.strip()
        cur['last_name'] = res[i].last_name.strip()
        dt = res[i].tweet_date
        cur['tweet_date'] = dt.strftime('%B %d at %H:%M') # ex: March 21 at 18:13
        cur['date_descriptor'] = descriptor

    for d in range(1, NUM_DISTRICTS + 1):
        for party in parties:
            dp_data = data[d][party]
            candidates = list(dp_data.keys())
            dp_data['combined'] = {}
            cur = dp_data['combined']
            if len(candidates) == 0:
                # it is possible to have 0 tweets about a candidate
                cur['total_likes'] = 0
                cur['num_tweets'] = 0
                cur['max_likes'] = 0
                cur['tweet_text'] = 'null'
                cur['first_name'] = 'null'
                cur['last_name'] = 'null'
                cur['tweet_date'] = 'null'
                cur['date_descriptor'] = 'null'
            else:
                cur['total_likes'] = sum([dp_data[c]['total_likes'] for c in candidates])
                cur['num_tweets'] = sum([dp_data[c]['num_tweets'] for c in candidates])
                max_idx = np.argmax([dp_data[c]['max_likes'] for c in candidates])
                max_c = candidates[max_idx]
                cur['max_likes'] = dp_data[max_c]['max_likes']
                cur['tweet_text'] = dp_data[max_c]['tweet_text']
                cur['first_name'] = dp_data[max_c]['first_name']
                cur['last_name'] = dp_data[max_c]['last_name']
                cur['tweet_date'] = dp_data[max_c]['tweet_date']
                cur['date_descriptor'] = dp_data[max_c]['date_descriptor']

    return data

def get_tweets_query(start, end):
    query = "SELECT DISTINCT tweets.tweet_id, tweets.district, tweets.party, tweets.candidate, T1.total_likes, T1.num_tweets, tweets.first_name, tweets.last_name, T1.max_likes, tweets.tweet_text, tweets.tweet_date \
                    FROM \
                        (SELECT tweets.district, tweets.party, tweets.candidate, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                        FROM tweets \
                        WHERE tweets.tweet_date BETWEEN '{}' AND '{}'    \
                        GROUP BY tweets.district, tweets.party, tweets.candidate) T1, tweets \
                    WHERE tweets.district = T1.district \
                    AND tweets.party = T1.party \
                    AND tweets.likes = T1.max_likes".format(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
    return query

def get_tweets_archive_query(start, end):
    query = "SELECT tweets_archive.tweet_id, tweets_archive.district, tweets_archive.party, tweets_archive.candidate, tweets_archive.total_likes, tweets_archive.num_tweets, tweets_archive.likes as max_likes, tweets_archive.most_liked_tweet as tweet_text, tweets_archive.first_name, tweets_archive.last_name, tweets_archive.week_start as tweet_date\
            FROM tweets_archive \
            WHERE tweets_archive.week_start \
            BETWEEN '{}' AND '{}'".format(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
    return query

def merge_tweets_and_tweet_archive(tweets_data, tweets_archive_data):
    parties = ['Democrat', 'Republican']
    data = {}
    for d in range(1, NUM_DISTRICTS + 1):
        data[d] = {}
        for party in parties:
            data[d][party] = {}
            dp_data = data[d][party]
            all_c = set(list(tweets_data[d][party].keys()) + list(tweets_archive_data[d][party].keys()))
            for c in all_c:
                if c == 'combined':
                    continue
                dp_data[c] = {}
                for col in ['total_likes', 'num_tweets']:
                    dp_data[c][col] = 0
                    if c in tweets_data[d][party]:
                        dp_data[c][col] += tweets_data[d][party][c][col]
                    if c in tweets_archive_data[d][party]:
                        dp_data[c][col] += tweets_archive_data[d][party][c][col]
                max_data = None
                if c not in tweets_data[d][party]:
                    max_data = tweets_archive_data
                elif c not in tweets_archive_data[d][party]:
                    max_data = tweets_data
                else:
                    max_data = tweets_data if tweets_data[d][party][c]['max_likes'] >= tweets_archive_data[d][party][c]['max_likes'] else tweets_archive_data
                dp_data[c]['max_likes'] = max_data[d][party][c]['max_likes']
                dp_data[c]['tweet_text'] = max_data[d][party][c]['tweet_text']
                dp_data[c]['first_name'] = max_data[d][party][c]['first_name']
                dp_data[c]['last_name'] = max_data[d][party][c]['last_name']
                dp_data[c]['tweet_date'] = max_data[d][party][c]['tweet_date']
                dp_data[c]['date_descriptor'] = max_data[d][party][c]['date_descriptor']

    for d in range(1, NUM_DISTRICTS + 1):
        for party in parties:
            dp_data = data[d][party]
            candidates = list(dp_data.keys())
            dp_data['combined'] = {}
            cur = dp_data['combined']
            if len(candidates) == 0:
                # it is possible to have 0 tweets about a candidate
                cur['total_likes'] = 0
                cur['num_tweets'] = 0
                cur['max_likes'] = 0
                cur['tweet_text'] = 'null'
                cur['first_name'] = 'null'
                cur['last_name'] = 'null'
                cur['tweet_date'] = 'null'
                cur['date_descriptor'] = 'null'
            else:
                cur['total_likes'] = sum([dp_data[c]['total_likes'] for c in candidates])
                cur['num_tweets'] = sum([dp_data[c]['num_tweets'] for c in candidates])
                max_idx = np.argmax([dp_data[c]['max_likes'] for c in candidates])
                max_c = candidates[max_idx]
                cur['max_likes'] = dp_data[max_c]['max_likes']
                cur['tweet_text'] = dp_data[max_c]['tweet_text']
                cur['first_name'] = dp_data[max_c]['first_name']
                cur['last_name'] = dp_data[max_c]['last_name']
                cur['tweet_date'] = dp_data[max_c]['tweet_date']
                cur['date_descriptor'] = dp_data[max_c]['date_descriptor']    

    return data

# Create your views here.
@csrf_exempt
def tweet_view(request):
    # Django's ORM is good but I couldn't figure out how to get the query below using it
    # query1 = Tweets.objects.values('district', 'party').annotate(total_likes = Sum('likes'), num_tweets = Count('tweet_id'), max_likes = Max('likes'))
     # objs_tf = Tweets.objects.filter(tweet_date__range = [start, end])

    # POST when daterange is queried
    if request.method == 'POST':
        # ex of request.body: daterange=March 5, 2017 - March 11, 2017
        daterange = request.body.decode('utf-8').split('=')[1]
        splits = daterange.split('-')
        start = splits[0].strip()
        end = splits[1].strip()
        start = datetime.strptime(start, '%B %d, %Y')
        end = datetime.strptime(end, '%B %d, %Y') + timedelta(days=1)
        query = None
        data = None
        if is_in_current_week(start, end):
            print('is current week')
            # uses Tweets db
            query = get_tweets_query(start, end)
            res = list(Tweets.objects.raw(query))
            data = serialize_results(res, 'exact')
        elif is_before_current_week(start, end):
            print('is prev week')
            # uses Tweets Archive table
            query = get_tweets_archive_query(start, end)
            res = list(TweetsArchive.objects.raw(query))
            data = serialize_results(res, 'weekly')
        else:
            print('need to merge')
            # run both and merge results
            query1 = get_tweets_query(start, end)
            query2 = get_tweets_archive_query(start, end)
            res1 = list(Tweets.objects.raw(query1))
            res2 = list(TweetsArchive.objects.raw(query2))
            data1 = serialize_results(res1, 'exact')
            data2 = serialize_results(res2, 'weekly')
            data = merge_tweets_and_tweet_archive(data1, data2)
            # print('data1', data1)
            # print('data2', data2)
            # print('data', data)

        return HttpResponse(json.dumps(data))

    # get HTML and base map with everything in Tweets (1w)
    else:
        res = list(Tweets.objects.raw(BASE_QUERY))
        data = serialize_results(res, 'exact')

        fp = open('tweets/data/illinois.json', 'rb')
        context = {
            'data': json.dumps(data),
            'map_json': json.dumps(json.load(fp))
        }
        fp.close()
        return render(request, 'templates/tweets_view.html', context)
