from django.db import models
from account.models import Webusers

# Create your models here.
class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Webusers, on_delete=models.DO_NOTHING, related_name='messages')
    content = models.CharField(max_length=500)
    page = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Messages'
        
class MessageReport(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Webusers, on_delete=models.DO_NOTHING, related_name='messagereport')
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MessageReport'