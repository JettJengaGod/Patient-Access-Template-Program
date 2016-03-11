# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-11 18:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PatientScheduling', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NurseScheduleGroups',
            fields=[
                ('Name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('UserCreated', models.BooleanField(default=True)),
                ('SavedDate', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SavedSchedule',
            fields=[
                ('Name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('SavedDate', models.DateTimeField(auto_now=True)),
                ('NurseSchedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.NurseScheduleGroups')),
            ],
        ),
        migrations.AlterField(
            model_name='appointment',
            name='ChairID',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='nurseschedule',
            name='NurseID',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='nurseschedule',
            name='ScheduleGroupName',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatientScheduling.NurseScheduleGroups'),
        ),
        migrations.DeleteModel(
            name='ScheduleGroups',
        ),
    ]
