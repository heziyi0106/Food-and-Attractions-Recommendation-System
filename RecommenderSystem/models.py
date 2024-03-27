from django.db import models
from account.models import Webusers
from message.models import Messages

# Create your models here.


class ShopsData(models.Model):
    shopName = models.CharField(max_length=50)
    shopAddress = models.CharField(max_length=200)
    shopPhone = models.CharField(max_length=50)
    shopHours = models.CharField(max_length=50)
    shopPhoto = models.CharField(max_length=50)
    shopType = models.CharField(max_length=5,default='0')

    class Meta:
        db_table = "shopsData"

class ShopsKeyWords(models.Model):
    shop = models.ForeignKey(ShopsData, on_delete=models.CASCADE)
    keyWords = models.CharField(max_length=300, null=True)
    contentGroup = models.CharField(max_length=300, null=True)
    contentGroupKeys = models.CharField(max_length=300, null=True)
    similarityScore = models.CharField(max_length=255,null=True)  # 儲存五個 item[1]
    similarityShop = models.CharField(max_length=255,null=True)   # 儲存五個 item[2]



    class Meta:
        db_table = "shopsKeyWords"


