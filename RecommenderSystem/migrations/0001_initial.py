# Generated by Django 4.2.8 on 2024-01-11 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ShopsData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("shopName", models.CharField(max_length=50)),
                ("address", models.CharField(max_length=200)),
                ("phone", models.CharField(max_length=50)),
                ("shopHours", models.CharField(max_length=50)),
                ("shopPhoto", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "shopsData",
            },
        ),
    ]
