# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-15 19:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('PatientScheduling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='EndTime',
            field=models.TimeField(default=datetime.datetime(2016, 2, 15, 19, 35, 53, 343529, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='StartTime',
            field=models.TimeField(default=datetime.datetime(2016, 2, 15, 19, 35, 59, 847738, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nurseschedule',
            name='EndTime',
            field=models.TimeField(default=datetime.datetime(2016, 2, 15, 19, 36, 2, 244031, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nurseschedule',
            name='LunchTime',
            field=models.TimeField(default=datetime.datetime(2016, 2, 15, 19, 36, 5, 221774, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nurseschedule',
            name='StartTime',
            field=models.TimeField(default=datetime.datetime(2016, 2, 15, 19, 36, 24, 823995, tzinfo=utc)),
            preserve_default=False,
        ),
    ]