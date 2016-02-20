# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-20 01:59
from __future__ import unicode_literals

import PatientScheduling.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PatientScheduling', '0004_auto_20160219_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleGroups',
            fields=[
                ('Name', models.CharField(max_length=20, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='nurseschedule',
            name='Team',
            field=models.CharField(default='A', max_length=1, validators=[PatientScheduling.models.model_one_letter]),
        ),
        migrations.AddField(
            model_name='nurseschedule',
            name='ScheduleGroupName',
            field=models.ForeignKey(default='group1', on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.ScheduleGroups'),
            preserve_default=False,
        ),
    ]