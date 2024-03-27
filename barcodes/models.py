from django.db import models

# Create your models here.


from django.db import models
from account.models import Webusers
from django.utils import timezone

# Create your models here.


class Stores(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "stores"


class Barcodes(models.Model):
    barcode_number = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(
        Webusers, on_delete=models.CASCADE,  null=False)
    store = models.ForeignKey(
        Stores, on_delete=models.CASCADE, null=False)
    face_price = models.CharField(max_length=50,  null=False)
    used_status = models.CharField(max_length=50, null=False)
    used_start = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=1), null=False)
    used_end = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=3), null=False)
    barcode_img0 = models.CharField(max_length=50, null=False)

    def save(self, *args, **kwargs):
        # 在保存时将时分秒部分设为零
        self.used_start = self.used_start.replace(
            hour=0, minute=0, second=0, microsecond=0)
        self.used_end = self.used_end.replace(
            hour=0, minute=0, second=0, microsecond=0)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "barcodes"
