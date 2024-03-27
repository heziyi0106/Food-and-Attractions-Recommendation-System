# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models



class PasswordResets(models.Model):
    reset_id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey('Webusers', models.DO_NOTHING)
    reset_token = models.CharField(max_length=255)
    token_expiration = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    was_used = models.IntegerField(default='0')

    class Meta:
        db_table = 'password_resets'


class RegisterVerify(models.Model):
    reset_id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey('Webusers', models.DO_NOTHING)
    verify_token = models.CharField(max_length=255)
    token_expiration = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'register_verify'

class Webusers(models.Model):
    user_id = models.AutoField(primary_key=True)
    account = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)
    username = models.CharField(max_length=50)
    birthday = models.DateField()
    email = models.CharField(unique=True, max_length=100)
    phone = models.CharField(unique=True, max_length=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.IntegerField(default=0)

    class Meta:
        db_table = 'webusers'
