# Generated by Django 3.2.18 on 2023-09-08 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gw2_tp', '0006_auto_20230908_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='items',
            name='sales_flag',
            field=models.BooleanField(default=False),
        ),
    ]
