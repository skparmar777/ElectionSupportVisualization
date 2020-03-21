To explore how to use the Django class, do the following:

#  starts special shell with a Django environment variable (settings) that is used to connect to the DB
python manage.py shell

# in the shell
from tweets.models import Tweets
objs = Tweets.objects.all()
objs
