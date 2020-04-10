To explore how to use the Django class, do the following:

#  starts special shell with a Django environment variable (settings) that is used to connect to the DB
python manage.py shell

# in the shell
from tweets.models import Tweets
objs = Tweets.objects.all()
objs

to insert a bunch of random tweets into the database, run:
    python manage.py shell

    from generate_fake_tweets import generate_and_push_tweets
    generate_and_push_tweets(1000)
