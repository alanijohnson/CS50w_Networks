# Generated by Django 3.1.6 on 2021-02-15 22:40

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20210215_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(default='', verbose_name='Enter Content'),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_posted',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 15, 22, 40, 58, 982708, tzinfo=utc), verbose_name='Date Posted'),
        ),
    ]
