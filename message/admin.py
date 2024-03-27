from django.contrib import admin
from message.models import Messages,MessageReport
# Register your models here.


class Messages_Admin(admin.ModelAdmin):
    list_display = ('id','user','content','page','created_at','updated_at')

class MessageReport_Admin(admin.ModelAdmin):
    list_display = ('id','user','title','content','created_at')


admin.site.register(Messages,Messages_Admin)
admin.site.register(MessageReport,Messages_Admin)