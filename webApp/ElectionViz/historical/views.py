from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Historical
from comments.comments import get_recent_comments

NUM_DISTRICTS = 102
BASE_QUERY = "SELECT * FROM historical"

def process_results(qset):
    # turn qset into a hierarchical dictionary for easy rendering
    data = {}
    for q in qset:
        year = q.year
        party = q.party.strip()
        candidate = q.candidate.strip()
        county = q.county
        votes = q.votes
        if year not in data:
            data[year] = {}
        if county not in data[year]:
            data[year][county] = {}
        if party not in data[year][county]:
            data[year][county][party] = {}
        if candidate not in data[year][county][party]:
            data[year][county][party][candidate] = 0
        data[year][county][party][candidate] = votes
    return data


# Create your views here.
@csrf_exempt
def historical_view(request):
    res = list(Historical.objects.raw(BASE_QUERY))
    data = process_results(res)    
    comments = get_recent_comments()
    fp = open('data/illinois.json', 'rb')
    context = {
        'data': json.dumps(data),
        'map_json': json.dumps(json.load(fp)),
        'comments': json.dumps(comments)
    }
    fp.close()
    return render(request, 'templates/historical_view.html', context)
