from datetime import datetime, timedelta
from django.db import connection
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import random
import json

from .models import Comments

MAX_HASH = 2**30

def compute_hash(password):
    # silly hash
    h = 0
    for c in password:
        i = ord(c)
        if i % 2 == 0:
            h += i
        else:
            h += i**2
    return h

def get_hash(password):
    random.seed(7)
    hpass = compute_hash(password)
    if hpass > MAX_HASH:
        while hpass > MAX_HASH:
            hpass = int(hpass / 2)
    elif hpass < -MAX_HASH:
        while hpass < -MAX_HASH:
            hpass = int(hpass / 2)
    return hpass

def validate_user(name, password):
    query = "SELECT * FROM comments \
            WHERE comments.name = '{}' AND comments.hpass = {}".format(name, get_hash(password))
    return len(list(Comments.objects.raw(query))) == 1

def check_user_exists(name):
    query = "SELECT * FROM comments \
            WHERE comments.name = '{}'".format(name)
    return len(list(Comments.objects.raw(query))) == 1

def get_recent_comments():
    one_day_ago = datetime.utcnow() + timedelta(days=-1)
    query = "SELECT * FROM comments \
            WHERE comments.comment_time > '{}' \
            ORDER BY comments.comment_time DESC".format(one_day_ago.strftime("%Y-%m-%d %H:%M:%S"))
    res = list(Comments.objects.raw(query))
    to_return = []
    for i in range(len(res)):
        name = res[i].name.strip()
        date = res[i].comment_time.strftime("%Y-%m-%d %H:%M:%S")
        comment = res[i].comment.strip()
        to_return.append({
            'name': name, 
            'date': date,
            'comment': comment
        })
    return to_return

def push_comment(name, password, comment):
    # true on success, false on failure
    if check_user_exists(name):
        return False
    now = datetime.utcnow()
    query = "INSERT INTO comments \
            VALUES ('{}', {}, '{}', '{}')".format(name, get_hash(password), now.strftime("%Y-%m-%d %H:%M:%S"), comment)
    with connection.cursor() as cursor:
        cursor.execute(query)
    return True

def delete_comment(name, password):
    # true on success, false on failure
    if validate_user(name, password) is False:
        return False
    query = "DELETE FROM comments \
            WHERE comments.name = '{}' \
            AND comments.hpass = {}".format(name, get_hash(password))
    with connection.cursor() as cursor:
        cursor.execute(query)
    return True

def update_comment(name, password, comment):
    # true on success, false on failure
    if validate_user(name, password) is False:
        return False
    now = datetime.utcnow()
    query = "UPDATE comments \
            SET comments.comment = '{}', comments.comment_time = '{}' \
            WHERE comments.name = '{}' \
            AND comments.hpass = {}".format(comment,now.strftime("%Y-%m-%d %H:%M:%S"), name, get_hash(password))
    with connection.cursor() as cursor:
        cursor.execute(query)
    return True

@csrf_exempt
def handle_comment_request(request):
    if request.method == "GET":
        return HttpResponse(json.dumps(get_recent_comments()))
    elif request.method != "POST":
        return HttpResponseBadRequest()
    items = request.body.decode('utf-8').split('&')
    data = {}
    for string in items:
        splits = string.split('=')
        data[splits[0]] = splits[1]
    print(data)

    # delete comment
    if 'undo' in data:
        # delete comment
        if 'name' not in data or 'password' not in data:
            return HttpResponseBadRequest()
        if delete_comment(data['name'], data['password']):
            return HttpResponse()
        else:
            return HttpResponseBadRequest()
    
    # insert or update
    if 'name' not in data or 'password' not in data or 'comment' not in data:
        return HttpResponseBadRequest()
    if check_user_exists(data['name']):
        # existing user, check password
        if update_comment(data['name'], data['password'], data['comment']):
            return HttpResponse()
        else:
            # bad password
            return HttpResponseBadRequest()
    elif push_comment(data['name'], data['password'], data['comment']):
        # valid new user
        return HttpResponse()
    else:
        # some problem occured
        return HttpResponseBadRequest()
