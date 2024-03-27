from django.contrib import admin
from member_management.models import Points,PointHistory
# Register your models here.

class Points_Admin(admin.ModelAdmin):
    list_display = ('id','user','havepoint','todaypoint','created_at')

class PointHistory_Admin(admin.ModelAdmin):
    list_display = ('id','user','point','content','updated_at')


admin.site.register(Points,Points_Admin)
admin.site.register(PointHistory,PointHistory_Admin)
