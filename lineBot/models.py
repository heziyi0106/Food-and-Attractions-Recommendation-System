from django.db import models
from account.models import Webusers
# Create your models here.

class LineAccountLink(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Webusers, on_delete=models.DO_NOTHING, related_name='lineaccountlink')
    lineid = models.CharField(max_length=100)
    nonce = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'LineAccountLink'
