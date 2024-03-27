from django.db import models
from account.models import Webusers

# Create your models here.
class Points(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Webusers, on_delete=models.DO_NOTHING, related_name='points')
    havepoint = models.IntegerField(default=0)
    todaypoint = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Points'

class PointHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Webusers, on_delete=models.DO_NOTHING, related_name='pointhistory')
    point = models.IntegerField(default=0)
    content = models.CharField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PointHistory'