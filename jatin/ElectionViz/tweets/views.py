from django.shortcuts import render
from django.db.models import Sum, Max, Count
import json

from .models import Tweets

# Create your views here.
def tweet_view(request):
    # Django's ORM is good but I couldn't figure out how to get the query below using it
    # query1 = Tweets.objects.values('district', 'party').annotate(total_likes = Sum('likes'), num_tweets = Count('tweet_id'), max_likes = Max('likes'))
    query = "SELECT tweets.tweet_id, tweets.district, tweets.party, T1.total_likes, T1.num_tweets, T1.max_likes, tweets.tweet_text, tweets.first_name, tweets.last_name \
            FROM \
                (SELECT tweets.district as district, tweets.party as party, SUM(tweets.likes) as total_likes, COUNT(*) as num_tweets, MAX(tweets.likes) as max_likes \
                FROM tweets \
                GROUP BY tweets.district, tweets.party) T1, tweets \
            WHERE tweets.district = T1.district \
            AND tweets.party = T1.party \
            AND tweets.likes = T1.max_likes"
    res = list(Tweets.objects.raw(query))

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
        data.append(new)

    fp = open('tweets/data/illinois.json', 'rb')
    context = {
        'data': json.dumps(data),
        'map_json': json.dumps(json.load(fp))
    }
    fp.close()
    return render(request, 'templates/tweets_view.html', context)
