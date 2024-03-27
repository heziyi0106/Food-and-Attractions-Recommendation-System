# Generated by Django 4.2.7 on 2024-01-31 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0004_rename_account_passwordresets_account_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('havepoint', models.IntegerField(default=0)),
                ('todaypoint', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='points', to='account.webusers')),
            ],
            options={
                'db_table': 'Points',
            },
        ),
        migrations.CreateModel(
            name='PointHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('point', models.IntegerField(default=0)),
                ('content', models.CharField(max_length=500)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pointhistory', to='account.webusers')),
            ],
            options={
                'db_table': 'PointHistory',
            },
        ),
    ]