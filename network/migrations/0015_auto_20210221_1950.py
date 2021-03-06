# Generated by Django 3.1.6 on 2021-02-21 19:50

import datetime
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0014_auto_20210221_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followmodel',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 21, 19, 50, 12, 414870, tzinfo=utc), verbose_name='Date Followed'),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_posted',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 21, 19, 50, 12, 412313, tzinfo=utc), verbose_name='Date Posted'),
        ),
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
