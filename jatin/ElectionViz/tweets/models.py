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
        db_table = 'Tweets'


# class TweetsArchive(models.Model):
#     tweet_id = models.AutoField(primary_key=True)
#     week_start = models.DateField(blank=True, null=True)
#     district = models.IntegerField(blank=True, null=True)
#     num_tweets = models.IntegerField(blank=True, null=True)
#     total_likes = models.IntegerField(blank=True, null=True)
#     party = models.CharField(max_length=100, blank=True, null=True)
#     candidate = models.CharField(max_length=100, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tweets_archive'
