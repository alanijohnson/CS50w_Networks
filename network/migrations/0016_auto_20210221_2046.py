# Generated by Django 3.1.6 on 2021-02-21 20:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0015_auto_20210221_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followmodel',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 21, 20, 46, 24, 738088, tzinfo=utc), verbose_name='Date Followed'),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(blank=True, default='', verbose_name='Enter Content'),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_posted',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 21, 20, 46, 24, 736928, tzinfo=utc), verbose_name='Date Posted'),
        ),
    ]
