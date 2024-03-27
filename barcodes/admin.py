from django.contrib import admin
from barcodes.models import Stores, Barcodes

# Register your models here.

class Stores_Admin(admin.ModelAdmin):
    list_display = ('store_id','store_name')

class Barcodes_Admin(admin.ModelAdmin):
    list_display = ('barcode_number','user','store','face_price','used_status','used_start','used_end','barcode_img0')

admin.site.register(Stores,Stores_Admin)
admin.site.register(Barcodes,Barcodes_Admin)
