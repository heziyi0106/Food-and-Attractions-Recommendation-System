# Generated by Django 4.1.6 on 2024-02-06 15:40

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0004_rename_account_passwordresets_account_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stores',
            fields=[
                ('store_id', models.AutoField(primary_key=True, serialize=False)),
                ('store_name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'stores',
            },
        ),
        migrations.CreateModel(
            name='Barcodes',
            fields=[
                ('barcode_number', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('face_price', models.CharField(max_length=50)),
                ('used_status', models.CharField(max_length=50)),
                ('used_start', models.DateTimeField(default=datetime.datetime(2024, 2, 7, 15, 40, 4, 998475, tzinfo=datetime.timezone.utc))),
                ('used_end', models.DateTimeField(default=datetime.datetime(2024, 3, 8, 15, 40, 4, 998475, tzinfo=datetime.timezone.utc))),
                ('barcode_img0', models.CharField(max_length=50)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barcodes.stores')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.webusers')),
            ],
            options={
                'db_table': 'barcodes',
            },
        ),
    ]
