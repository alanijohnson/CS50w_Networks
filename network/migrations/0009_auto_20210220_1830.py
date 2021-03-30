# Generated by Django 3.1.6 on 2021-02-20 18:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_auto_20210218_0007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='followmodel',
            old_name='user',
            new_name='follower',
        ),
        migrations.AlterField(
            model_name='followmodel',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 20, 18, 30, 14, 368686, tzinfo=utc), verbose_name='Date Followed'),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_posted',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 20, 18, 30, 14, 368210, tzinfo=utc), verbose_name='Date Posted'),
        ),
        migrations.AlterUniqueTogether(
            name='followmodel',
            unique_together={('follower', 'following')},
        ),
    ]
