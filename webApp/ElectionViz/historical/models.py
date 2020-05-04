from django.db import models

# Create your models here.
class Historical(models.Model):
    year = models.IntegerField(primary_key=True)
    party = models.CharField(max_length=100)
    candidate = models.CharField(max_length=100)
    county = models.IntegerField()
    votes = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'historical'
        unique_together = (('year', 'party', 'candidate', 'county'),)
