from django.shortcuts import render
from django.db.models import Avg, Max, Count
import json

from .models import Tweets

# Create your views here.
def tweet_view(request):
    query = Tweets.objects.values('district', 'party').annotate(avg_likes = Avg('likes'), num_tweets = Count('tweet_id'))
    res = list(query)
    columns = ['district', 'party', 'avg_likes', 'num_tweets']
    data = []
    for i in range(len(res)):
        new = {}
        for k in columns:
            if type(res[i][k]) == str:
                # cleans data
                new[k] = res[i][k].strip()
            else:
                new[k] = str(res[i][k])
        data.append(new)

    fp = open('tweets/data/illinois.json', 'rb')
    context = {
        'data': json.dumps(data),
        'map_json': json.dumps(json.load(fp))
    }
    fp.close()
    return render(request, 'templates/tweets_view.html', context)
