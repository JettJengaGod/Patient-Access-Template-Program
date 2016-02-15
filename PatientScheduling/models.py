from django.db import models


class Nurse(models.Model):
    ID = models.AutoField(primary_key=True)


class NurseSchedule(models.Model):
    #  models.AutoField(primary_key=True) is a default field
    NurseID = models.ForeignKey(Nurse)
    ScheduleGroup = models.TextField
    StartTime = models.TimeField(auto_now=False, default='8:00')
    LunchTime = models.TimeField(auto_now=False, default='12:00')
    LunchDuration = models.PositiveIntegerField(default=60)
    EndTime = models.TimeField(auto_now=False, default='5:00')


class Appointment(models.Model):
    # models.AutoField(primary_key=True) is a default field
    NurseScheduleID = models.ForeignKey(NurseSchedule)
    StartTime = models.TimeField(auto_now=False)
    EndTime = models.TimeField(auto_now=False)
