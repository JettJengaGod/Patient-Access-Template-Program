from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User


def model_one_letter(value):
    if not value.isupper():
        raise ValidationError(
            _('%(value) is not an upper case letter'),
            params={'value': value},
        )

# Company Start and End work hours
class MinMaxTime(models.Model):
    MinTime = models.TimeField(auto_now=False)
    MaxTime = models.TimeField(auto_now=False)

    def __unicode__(self):
        # return u"start {0} and end {1}".format(self.MinTime, self.MaxTime)
        return u'%s %s' % (self.MinTime, self.MaxTime)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # CompanyHours = models.OneToOneField(MinMaxTime)


class NurseScheduleGroups(models.Model):
    Name = models.CharField(max_length=20, primary_key=True)
    UserCreated = models.BooleanField(default=True)
    SavedDate = models.DateTimeField(auto_now=True)


class SavedSchedule(models.Model):
    Name = models.CharField(max_length=20, primary_key=True)
    SavedDate = models.DateTimeField(auto_now=True)
    NurseSchedule = models.ForeignKey(NurseScheduleGroups)


class NurseSchedule(models.Model):
    # models.AutoField(primary_key=True) is a default field
    NurseID = models.PositiveIntegerField(null=True)
    Team = models.CharField(max_length=1, default='A', validators=[model_one_letter])
    ScheduleGroupName = models.ForeignKey(NurseScheduleGroups)
    StartTime = models.TimeField(auto_now=False, default='8:00')
    LunchTime = models.TimeField(auto_now=False, default='12:00')
    LunchDuration = models.PositiveIntegerField(default=60)
    EndTime = models.TimeField(auto_now=False, default='16:00')


class Appointment(models.Model):
    # models.AutoField(primary_key=True) is a default field
    SavedSchedule = models.ForeignKey(SavedSchedule)
    NurseScheduleID = models.PositiveIntegerField(default=0)
    ChairID = models.PositiveIntegerField(default=0)
    StartTime = models.TimeField(auto_now=False)
    EndTime = models.TimeField(auto_now=False)
