from django.contrib import admin
from RecommenderSystem.models import ShopsData,ShopsKeyWords
# Register your models here.

class ShopsData_Admin(admin.ModelAdmin):
    list_display = ('id','shopName','shopAddress','shopPhone','shopHours','shopPhoto','shopType')

class ShopsData_Admin(admin.ModelAdmin):
    list_display = ('id','shop_id','keyWords','shopPhone','contentGroup','contentGroupKeys','similarityScore','similarityShop')


admin.site.register(ShopsData,ShopsData_Admin)
admin.site.register(ShopsKeyWords,ShopsData_Admin)
