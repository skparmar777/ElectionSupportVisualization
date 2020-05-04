from django.db import models

class Comments(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    hpass = models.IntegerField(blank=True, null=True)
    comment_time = models.DateTimeField(blank=True, null=True)
    comment = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'
        