from django.db import models

# Create your models here.
class Tweets(models.Model):
    tweet_id = models.AutoField(primary_key=True)
    tweet_date = models.DateTimeField(blank=True, null=True)
    district = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    party = models.CharField(max_length=100, blank=True, null=True)
    candidate = models.CharField(max_length=100, blank=True, null=True)
    tweet_text = models.CharField(max_length=560, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tweets'

class TweetsArchive(models.Model):
    week_start = models.DateField(primary_key=True)
    district = models.IntegerField()
    party = models.CharField(max_length=100)
    candidate = models.CharField(max_length=100)
    num_tweets = models.IntegerField(blank=True, null=True)
    total_likes = models.IntegerField(blank=True, null=True)
    most_liked_tweet = models.CharField(max_length=560, blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tweets_archive'
        unique_together = (('week_start', 'district', 'party', 'candidate'),)
