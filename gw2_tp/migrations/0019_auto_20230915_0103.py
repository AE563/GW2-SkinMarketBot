# Generated by Django 3.2.18 on 2023-09-15 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gw2_tp', '0018_auto_20230915_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leftovers',
            name='currently_available',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='price',
            name='maximum_price',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='price',
            name='price_now',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='price',
            name='selling_price',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
