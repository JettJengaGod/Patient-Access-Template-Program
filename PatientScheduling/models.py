from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models


def model_one_letter(value):
    if not value.isupper():
        raise ValidationError(
            _('%(value) is not an upper case letter'),
            params={'value': value},
        )


class NurseSchedule(models.Model):
    NurseID = models.AutoField(primary_key=True)
    Team = models.CharField(max_length=1, default='A', validators=[model_one_letter])
    ScheduleGroup = models.TextField  # used when loading saved schedules
    StartTime = models.TimeField(auto_now=False, default='8:00', blank=False)
    LunchTime = models.TimeField(auto_now=False, default='12:00')
    LunchDuration = models.PositiveIntegerField(default=60)
    EndTime = models.TimeField(auto_now=False, default='16:00')


class Appointment(models.Model):
    # models.AutoField(primary_key=True) is a default field
    NurseScheduleID = models.ForeignKey(NurseSchedule)
    StartTime = models.TimeField(auto_now=False)
    EndTime = models.TimeField(auto_now=False)
