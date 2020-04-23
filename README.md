# ElectionSupportVisualization

## Backend
The commands used to build the SQL database can be found in `backend/sql_commands.txt`. This will run a locally-hosted MSSQL server in a docker container.

## Django
Navigate to `webApp/ElectionViz`. To run the server:

```
python manage.py runserver
```

To push fake tweets, do:

```
python manage.py shell
```
```
# in the shell
from tweets.models import Tweets
objs = Tweets.objects.all()
objs

to insert a bunch of random tweets into the database, run:
    python manage.py shell

    from generate_fake_tweets import generate_and_push_tweets
    generate_and_push_tweets(1000)
```

