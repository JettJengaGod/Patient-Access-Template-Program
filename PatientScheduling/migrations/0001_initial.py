# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-25 21:31
from __future__ import unicode_literals

import PatientScheduling.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('NurseScheduleID', models.PositiveIntegerField(default=0)),
                ('ChairID', models.PositiveIntegerField(default=0)),
                ('StartTime', models.TimeField()),
                ('EndTime', models.TimeField()),
                ('SaveName', models.CharField(max_length=20, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='ChemotherapyDrug',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=60, unique=True)),
                ('EarliestTime', models.TimeField(null=True)),
                ('LatestTime', models.TimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NurseSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NurseID', models.PositiveIntegerField(null=True)),
                ('Team', models.CharField(default=b'A', max_length=1, validators=[PatientScheduling.models.model_one_letter])),
                ('StartTime', models.TimeField(default=b'08:00')),
                ('LunchTime', models.TimeField(default=b'12:00', null=True)),
                ('LunchDuration', models.PositiveIntegerField(default=60, null=True)),
                ('EndTime', models.TimeField(default=b'16:00')),
            ],
        ),
        migrations.CreateModel(
            name='NurseScheduleGroups',
            fields=[
                ('Name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('Chairs', models.IntegerField()),
                ('UserCreated', models.BooleanField(default=True)),
                ('SavedDate', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SavedSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=20, unique=True)),
                ('SavedDate', models.DateTimeField(auto_now=True)),
                ('NurseSchedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.NurseScheduleGroups')),
            ],
        ),
        migrations.CreateModel(
            name='SavedTimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=20)),
                ('SavedDate', models.DateTimeField(auto_now=True)),
                ('Duration', models.IntegerField(default=0)),
                ('Count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='nurseschedule',
            name='ScheduleGroupName',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.NurseScheduleGroups'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='SavedSchedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.SavedSchedule'),
        ),
    ]
