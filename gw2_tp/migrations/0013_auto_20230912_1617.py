# Generated by Django 3.2.18 on 2023-09-12 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gw2_tp', '0012_auto_20230911_2033'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leftovers',
            old_name='item_num',
            new_name='item_id',
        ),
        migrations.RenameField(
            model_name='price',
            old_name='item',
            new_name='item_id',
        ),
    ]
