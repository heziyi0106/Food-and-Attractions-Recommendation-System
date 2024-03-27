from django.contrib import admin
from lineBot.models import LineAccountLink

class LineAccountLink_Admin(admin.ModelAdmin):
    list_display = ('id','user_id','lineid','nonce','created_at')


admin.site.register(LineAccountLink,LineAccountLink_Admin)
# Register your models here.
