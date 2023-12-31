# Generated by Django 3.2.18 on 2023-09-15 01:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gw2_tp', '0017_alter_items_skin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buys',
            name='item_id',
        ),
        migrations.RemoveField(
            model_name='currentsells',
            name='item_id',
        ),
        migrations.RemoveField(
            model_name='sells',
            name='item_id',
        ),
        migrations.AddField(
            model_name='buys',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='gw2_tp.items'),
        ),
        migrations.AddField(
            model_name='currentsells',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='gw2_tp.items'),
        ),
        migrations.AddField(
            model_name='sells',
            name='item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='gw2_tp.items'),
        ),
        migrations.AlterField(
            model_name='items',
            name='description',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='items',
            name='icon',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='items',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
