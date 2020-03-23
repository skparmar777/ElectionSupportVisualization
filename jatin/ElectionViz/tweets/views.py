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

BASE_QUERY = "SELECT tweets.tweet_id, tweets.district, tweets.party, tweets.candidate, T1.total_likes, T1.num_tweets, tweets.first_name, tweets.last_name, T1.max_likes, tweets.tweet_text, tweets.tweet_date \
            FROM \
                (SELECT tweets.district, tweets.party, tweets.candidate, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                FROM tweets \
                GROUP BY tweets.district, tweets.party, tweets.candidate) T1, tweets \
            WHERE tweets.district = T1.district \
            AND tweets.party = T1.party \
            AND tweets.candidate = T1.candidate \
            AND tweets.likes = T1.max_likes"

NUM_DISTRICTS = 18

def get_previous_monday(dt):
    return dt + timedelta(days=-dt.weekday(), hours=-dt.hour, minutes=-dt.minute, seconds=-dt.second, microseconds=-dt.microsecond)

def get_tweets_cutoff(dt):
    return dt + timedelta(days=-6, hours=-dt.hour, minutes=-dt.minute, seconds=-dt.second, microseconds=-dt.microsecond)

def is_in_current_week(start, end):
    last_monday = get_previous_monday(datetime.utcnow())
    return start >= last_monday

def is_before_current_week(start, end):
    cutoff = get_tweets_cutoff(datetime.utcnow())
    return end < cutoff

def get_data_as_dict(res_item):
    cur = {}
    cur['total_likes'] = res_item.total_likes
    cur['num_tweets'] = res_item.num_tweets
    cur['max_likes'] = res_item.max_likes
    cur['tweet_text'] = res_item.tweet_text.strip()
    cur['first_name'] = res_item.first_name.strip()
    cur['last_name'] = res_item.last_name.strip()
    dt = res_item.tweet_date
    cur['tweet_date'] = dt.strftime('%B %d at %H:%M') # ex: March 21 at 18:13
    return cur

def merge_candidate_dicts(d1, d2):
    '''
    Merges data of two dicts of the same candidate from different weeks
    '''
    ret = {}
    ret['total_likes'] = d1['total_likes'] + d2['total_likes']
    ret['num_tweets'] = d1['num_tweets'] + d2['num_tweets']
    max_dict = d1 if d1['max_likes'] > d2['max_likes'] else d2
    ret['max_likes'] = max_dict['max_likes']
    ret['tweet_text'] = max_dict['tweet_text']
    ret['first_name'] = max_dict['first_name']
    ret['last_name'] = max_dict['last_name']
    ret['tweet_date'] = max_dict['tweet_date']
    ret['date_descriptor'] = max_dict['date_descriptor']
    return ret

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
        cur = get_data_as_dict(res[i])
        cur['date_descriptor'] = descriptor
        if candidate in data[district][party] and descriptor != 'exact': # if descriptor is exact, ignore possible duplicates
            # happens when there are multiple weeks (tweets_archive table)
            cur = merge_candidate_dicts(data[district][party][candidate], cur)
        data[district][party][candidate] = cur

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
    query = "SELECT tweets.tweet_id, tweets.district, tweets.party, tweets.candidate, T1.total_likes, T1.num_tweets, tweets.first_name, tweets.last_name, T1.max_likes, tweets.tweet_text, tweets.tweet_date \
                    FROM \
                        (SELECT tweets.district, tweets.party, tweets.candidate, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                        FROM tweets \
                        WHERE tweets.tweet_date BETWEEN '{}' AND '{}'    \
                        GROUP BY tweets.district, tweets.party, tweets.candidate) T1, tweets \
                    WHERE tweets.district = T1.district \
                    AND tweets.party = T1.party \
                    AND tweets.candidate = T1.candidate \
                    AND tweets.likes = T1.max_likes".format(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
    # print(query)
    return query

def get_tweets_archive_query(start, end):
    start = get_previous_monday(start) if start.weekday() != 0 else start # if not already a monday
    query = "SELECT tweets_archive.week_start, tweets_archive.week_start as tweet_date, tweets_archive.district, tweets_archive.party, tweets_archive.candidate, tweets_archive.total_likes, tweets_archive.num_tweets, tweets_archive.likes as max_likes, tweets_archive.most_liked_tweet as tweet_text, tweets_archive.first_name, tweets_archive.last_name\
            FROM tweets_archive \
            WHERE tweets_archive.week_start \
            BETWEEN '{}' AND '{}'".format(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
    # print(query)
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

def find_all_candidates(data):
    democrat_candidates = set()
    republican_candidates = set()
    for i in range(1, NUM_DISTRICTS + 1):
        for k in data[i]['Democrat'].keys():
            if k == 'combined':
                continue
            democrat_candidates.add(k)
        for k in data[i]['Republican'].keys():
            if k == 'combined':
                continue
            republican_candidates.add(k)
    return list(democrat_candidates), list(republican_candidates)

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
        end = datetime.strptime(end, '%B %d, %Y') + timedelta(hours=23, minutes=59, seconds=59)
        query = None
        data = None
        if is_in_current_week(start, end):
            # print('is cur week')
            # uses Tweets db
            query = get_tweets_query(start, end)
            res = list(Tweets.objects.raw(query))
            data = serialize_results(res, 'exact')
        elif is_before_current_week(start, end):
            # print('is prev week')
            # uses Tweets Archive table
            query = get_tweets_archive_query(start, end)
            res = list(TweetsArchive.objects.raw(query))
            data = serialize_results(res, 'weekly')
        else:
            # print('need to merge')
            # run both and merge results
            query1 = get_tweets_query(start, end)
            query2 = get_tweets_archive_query(start, end)
            res1 = list(Tweets.objects.raw(query1))
            res2 = list(TweetsArchive.objects.raw(query2))
            data1 = serialize_results(res1, 'exact')
            data2 = serialize_results(res2, 'weekly')
            data = merge_tweets_and_tweet_archive(data1, data2)
        return HttpResponse(json.dumps(data))

    # get HTML and base map with everything in Tweets (1w)
    else:
        res = list(Tweets.objects.raw(BASE_QUERY))
        data = serialize_results(res, 'exact')
        democrat_candidates, republican_candidates = find_all_candidates(data)
        fp = open('tweets/data/illinois.json', 'rb')
        context = {
            'data': json.dumps(data),
            'democrat_candidates': json.dumps(democrat_candidates),
            'republican_candidates': json.dumps(republican_candidates),
            'map_json': json.dumps(json.load(fp))
        }
        fp.close()
        return render(request, 'templates/tweets_view.html', context)
