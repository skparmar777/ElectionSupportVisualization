from django.shortcuts import render
from django.db.models import Sum, Max, Count
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from datetime import timezone
import json

from .data_utils import TweetsData, Candidate, CandidatePolarity, Party
from .models import Tweets, TweetsArchive
from .comments import get_recent_comments
import numpy as np

NUM_DISTRICTS = 18

# I tried using the Django ORM but the query I want I just could not find anywhere
BASE_QUERY = "SELECT tweets.tweet_id, tweets.tweet_date, tweets.district, tweets.party, tweets.candidate, tweets.polarity, T1.total_likes, T1.num_tweets, T1.avg_sentiment, tweets.username, T1.max_likes, tweets.tweet_text, tweets.sentiment \
            FROM \
                (SELECT tweets.district, tweets.party, tweets.candidate, tweets.polarity, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes, AVG(tweets.sentiment) AS avg_sentiment \
                FROM tweets \
                GROUP BY tweets.district, tweets.party, tweets.candidate, tweets.polarity) T1, tweets \
            WHERE tweets.district = T1.district \
            AND tweets.party = T1.party \
            AND tweets.candidate = T1.candidate \
            AND tweets.polarity = T1.polarity \
            AND tweets.likes = T1.max_likes "
    

def get_tweets_query(start, end):
    query = "SELECT tweets.tweet_id, tweets.tweet_date, tweets.district, tweets.party, tweets.candidate, tweets.polarity, T1.total_likes, T1.num_tweets, T1.avg_sentiment, \
            tweets.username, T1.max_likes, tweets.tweet_text, tweets.sentiment \
            FROM \
                (SELECT tweets.district, tweets.party, tweets.candidate, tweets.polarity, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes, AVG(tweets.sentiment) AS avg_sentiment \
                FROM tweets \
                WHERE tweets.tweet_date BETWEEN '{}' AND '{}' \
                GROUP BY tweets.district, tweets.party, tweets.candidate, tweets.polarity) T1, tweets \
            WHERE tweets.district = T1.district \
            AND tweets.party = T1.party \
            AND tweets.candidate = T1.candidate \
            AND tweets.polarity = T1.polarity \
            AND tweets.likes = T1.max_likes".format(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
    return query

def get_tweets_archive_query(start, end):
    start = get_previous_monday(start) if start.weekday() != 0 else start # if not already a monday
    query = "SELECT tweets_archive.week_start, tweets_archive.week_start as tweet_date, tweets_archive.district, tweets_archive.party, tweets_archive.candidate, \
            tweets_archive.polarity, tweets_archive.total_likes, tweets_archive.num_tweets, tweets_archive.avg_sentiment, \
            tweets_archive.username, tweets_archive.likes, tweets_archive.tweet_text as tweet_text, tweets_archive.sentiment \
            FROM tweets_archive \
            WHERE tweets_archive.week_start \
            BETWEEN '{}' AND '{}'".format(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
    return query

def get_previous_monday(dt):
    return dt + timedelta(days=-dt.weekday(), hours=-dt.hour, minutes=-dt.minute, seconds=-dt.second, microseconds=-dt.microsecond)

def get_tweets_cutoff(dt):
    return dt + timedelta(days=-6, hours=-dt.hour, minutes=-dt.minute, seconds=-dt.second, microseconds=-dt.microsecond)

def is_within_one_week_ago(start, end):
    now = datetime.utcnow()
    one_week_ago = now + timedelta(days=-7, hours = -now.hour, minutes = -now.minute, seconds = -now.second, microseconds = -now.microsecond)
    return start >= one_week_ago

def is_before_current_week(start, end):
    cutoff = get_tweets_cutoff(datetime.utcnow())
    return end < cutoff

def process_results(qset, date_descriptor, asdict=True):
    '''
    qset: queryset from Tweets or TweetsArchive
    date_descriptor: whether date is 'exact' or 'weekly'

    Format: DISTRICT->PARTY->CANDIDATE->[total_likes, num_tweets, max_likes, tweet_text, username]
    each DPC also has a POS/NEG subcategory with the same above attributes for sentiment visualization
    Also, each DP gets a 'combined' category for cross-party comparisons. This also has a POS/NEG subcategory.
    '''
    parties = ['Democrat', 'Republican']
    data = {}
    for d in range(1, NUM_DISTRICTS + 1):
        data[d] = {}
        for party in parties:
            data[d][party] = {}

    for q in qset:
        # tweet: TweetsData instance
        # cp: CandidatePolarity instance
        # cd: Candidate instance
        tweet = TweetsData(q.username.strip(), q.tweet_text.strip(), q.likes, q.sentiment, q.tweet_date, date_descriptor)
        cp = CandidatePolarity(q.polarity.strip(), q.total_likes, q.num_tweets, q.avg_sentiment, tweet)
        district, party, candidate = q.district, q.party.strip(), q.candidate.strip()
        cd = None
        if candidate in data[district][party]:
            cd = data[district][party][candidate]
        else:
            cd = Candidate(candidate)
            data[district][party][candidate] = cd
        cd.insert_polarity(cp)
    
    for d in range(1, NUM_DISTRICTS + 1):
        district_data = data[d]
        for party in parties:
            py = Party(party)
            candidates = list(district_data[party].values())
            for c in candidates:
                c.combine_pos_neg()
                py.add_candidate(c)
            py.combine_candidates()
            if asdict:
                district_data[party] = py.asdict()
            else:
                district_data[party] = py

    return data


def find_all_candidates(data):
    democrat_candidates = set()
    republican_candidates = set()
    for i in range(1, NUM_DISTRICTS + 1):
        if data[i]['Democrat'] != 'null':
            for k in data[i]['Democrat'].keys():
                if k == 'combined':
                    continue
                democrat_candidates.add(k)
        if data[i]['Republican'] != 'null':
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

    # POST when daterange is queried; no other POST should come here
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
        if is_within_one_week_ago(start, end):
            # print('is cur week')
            # uses Tweets db
            query = get_tweets_query(start, end)
            res = list(Tweets.objects.raw(query))
            data = process_results(res, 'exact', asdict=True)
        elif is_before_current_week(start, end):
            # print('is prev week')
            # uses Tweets Archive table
            query = get_tweets_archive_query(start, end)
            res = list(TweetsArchive.objects.raw(query))
            data = process_results(res, 'weekly', asdict=True)
        else:
            # print('need to merge')
            # run both and merge results
            query1 = get_tweets_query(start, end)
            query2 = get_tweets_archive_query(start, end)
            res1 = list(Tweets.objects.raw(query1))
            res2 = list(TweetsArchive.objects.raw(query2))
            data1 = process_results(res1, 'exact', asdict=False)
            data2 = process_results(res2, 'weekly', asdict=False)
            # this combines the two dictionaries
            data = {}
            for d in range(1, NUM_DISTRICTS + 1):
                data[d] = {}
                for party in ['Democrat', 'Republican']:
                    data[d][party] = data1[d][party].combine(data2[d][party]).asdict()
            
        return HttpResponse(json.dumps(data))

    # get HTML and base map with everything in Tweets (1w)
    else:
        res = list(Tweets.objects.raw(BASE_QUERY))
        data = process_results(res, 'exact', asdict=True)    
        democrat_candidates, republican_candidates = ["Bernie", "Biden"], ['Trump'] # find_all_candidates(data)
        comments = get_recent_comments()
        fp = open('tweets/data/illinois.json', 'rb')
        context = {
            'data': json.dumps(data),
            'democrat_candidates': json.dumps(democrat_candidates),
            'republican_candidates': json.dumps(republican_candidates),
            'map_json': json.dumps(json.load(fp)),
            'comments': json.dumps(comments)
        }
        fp.close()
        return render(request, 'templates/tweets_view.html', context)
