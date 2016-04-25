from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models


def model_one_letter(value):
    if not value.isupper():
        raise ValidationError(
            _('%(value) is not an upper case letter'),
            params={'value': value},
        )


class NurseScheduleGroups(models.Model):
    Name = models.CharField(max_length=20, primary_key=True)
    UserCreated = models.BooleanField(default=True)
    SavedDate = models.DateTimeField(auto_now=True)


class SavedSchedule(models.Model):
    # models.AutoField(primary_key=True) is a default field
    Name = models.CharField(max_length=20, unique=True)
    SavedDate = models.DateTimeField(auto_now=True)
    NurseSchedule = models.ForeignKey(NurseScheduleGroups)


class NurseSchedule(models.Model):
    # models.AutoField(primary_key=True) is a default field
    NurseID = models.PositiveIntegerField(null=True)
    Team = models.CharField(max_length=1, default='A', validators=[model_one_letter])
    ScheduleGroupName = models.ForeignKey(NurseScheduleGroups)
    StartTime = models.TimeField(auto_now=False, default='08:00')
    LunchTime = models.TimeField(auto_now=False, default='12:00', null=True)
    LunchDuration = models.PositiveIntegerField(default=60, null=True)
    EndTime = models.TimeField(auto_now=False, default='16:00')


class SavedTimeSlot(models.Model):
    # models.AutoField(primary_key=True) is a default field
    Name = models.CharField(max_length=20, unique=False)
    SavedDate = models.DateTimeField(auto_now=True)
    Duration = models.IntegerField(default=0)
    Count = models.IntegerField(default=0)


class Appointment(models.Model):
    # models.AutoField(primary_key=True) is a default field
    SavedSchedule = models.ForeignKey(SavedSchedule)
    NurseScheduleID = models.PositiveIntegerField(default=0)
    ChairID = models.PositiveIntegerField(default=0)
    StartTime = models.TimeField(auto_now=False)
    EndTime = models.TimeField(auto_now=False)
    SaveName = models.CharField(max_length=20, primary_key=True)


