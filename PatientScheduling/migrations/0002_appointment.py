# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 04:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PatientScheduling', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NurseScheduleID', models.PositiveIntegerField(default=0)),
                ('ChairID', models.PositiveIntegerField(default=0)),
                ('StartTime', models.TimeField()),
                ('EndTime', models.TimeField()),
                ('SaveName', models.CharField(max_length=20)),
                ('SavedSchedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.SavedSchedule')),
            ],
        ),
    ]
