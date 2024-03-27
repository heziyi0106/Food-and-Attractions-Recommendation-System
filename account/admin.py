from django.contrib import admin
from account.models import PasswordResets,RegisterVerify,Webusers
# Register your models here.

class PasswordResets_Admin(admin.ModelAdmin):
    list_display = ('reset_id','account_id','reset_token','token_expiration','created_at','was_used')

class RegisterVerify_Admin(admin.ModelAdmin):
    list_display = ('reset_id','account_id','verify_token','token_expiration','created_at')

class Webusers_Admin(admin.ModelAdmin):
    list_display = ('user_id','account','password','gender','username','birthday','email','phone','created_at','updated_at','is_active')

admin.site.register(PasswordResets,PasswordResets_Admin)
admin.site.register(RegisterVerify,RegisterVerify_Admin)
admin.site.register(Webusers,RegisterVerify_Admin)