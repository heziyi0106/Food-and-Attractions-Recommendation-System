# Generated by Django 4.2.8 on 2024-02-13 17:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barcodes', '0010_alter_barcodes_used_end_alter_barcodes_used_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barcodes',
            name='used_end',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 16, 17, 45, 42, 658202, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='barcodes',
            name='used_start',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 14, 17, 45, 42, 658202, tzinfo=datetime.timezone.utc)),
        ),
    ]
