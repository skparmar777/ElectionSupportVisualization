from django.db import models

class Tweets(models.Model):
    tweet_id = models.AutoField(primary_key=True)
    tweet_date = models.DateTimeField(blank=True, null=True)
    party = models.CharField(max_length=100, blank=True, null=True)
    candidate = models.CharField(max_length=100, blank=True, null=True)
    district = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    tweet_text = models.CharField(max_length=560, blank=True, null=True)
    sentiment = models.FloatField(blank=True, null=True)
    polarity = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tweets'

class TweetsArchive(models.Model):
    week_start = models.DateField(primary_key=True)
    party = models.CharField(max_length=100)
    candidate = models.CharField(max_length=100)
    district = models.IntegerField()
    num_tweets = models.IntegerField(blank=True, null=True)
    total_likes = models.IntegerField(blank=True, null=True)
    average_sentiment = models.FloatField(blank=True, null=True)
    polarity = models.CharField(max_length=1)
    username = models.CharField(max_length=256, blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    tweet_text = models.CharField(max_length=560, blank=True, null=True)
    sentiment = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tweets_archive'
        unique_together = (('week_start', 'party', 'candidate', 'district', 'polarity'),)

class Comments(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    hpass = models.IntegerField(blank=True, null=True)
    comment_time = models.DateTimeField(blank=True, null=True)
    comment = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'
