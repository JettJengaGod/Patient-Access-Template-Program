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
    Chairs = models.IntegerField(null=False)
    UserCreated = models.BooleanField(default=True)
    SavedDate = models.DateTimeField(auto_now=True, verbose_name="Created On")

    class Meta:
        verbose_name_plural = "RN Schedules"
        verbose_name = "RN Schedule"


class SavedTimeSlotGroup(models.Model):
    Name = models.CharField(max_length=20, primary_key=True)
    SavedDate = models.DateTimeField(auto_now=True, verbose_name="Created On")

    class Meta:
        verbose_name_plural = "Saved Time Slots Inputs"
        verbose_name = "Time Slots Input"


class SavedSchedule(models.Model):
    # models.AutoField(primary_key=True) is a default field
    Name = models.CharField(max_length=20, unique=True)
    SavedDate = models.DateTimeField(auto_now=True)
    NurseSchedule = models.ForeignKey(NurseScheduleGroups, null=False, on_delete=models.CASCADE)
    TimeSlots = models.ForeignKey(SavedTimeSlotGroup, null=False, on_delete=models.CASCADE)


class NurseSchedule(models.Model):
    # models.AutoField(primary_key=True) is a default field
    NurseID = models.PositiveIntegerField(null=True)
    Team = models.CharField(max_length=1, default='A', validators=[model_one_letter])
    ScheduleGroupName = models.ForeignKey(NurseScheduleGroups, null=False, on_delete=models.CASCADE, editable=False)
    StartTime = models.TimeField(auto_now=False, default='08:00')
    LunchTime = models.TimeField(auto_now=False, default='12:00', null=True)
    LunchDuration = models.PositiveIntegerField(default=60, null=True)
    EndTime = models.TimeField(auto_now=False, default='16:00')


class SavedTimeSlot(models.Model):
    # models.AutoField(primary_key=True) is a default field
    Duration = models.IntegerField(default=0)
    Count = models.IntegerField(default=0)
    Group = models.ForeignKey(SavedTimeSlotGroup, null=False, on_delete=models.CASCADE)


class Appointment(models.Model):
    SavedSchedule = models.ForeignKey(SavedSchedule)
    NurseScheduleID = models.PositiveIntegerField(default=0)
    ChairID = models.PositiveIntegerField(default=0)
    StartTime = models.TimeField(auto_now=False)
    EndTime = models.TimeField(auto_now=False)
    SaveName = models.CharField(max_length=20)


class ChemotherapyDrug(models.Model):
    Name = models.CharField(primary_key=True, max_length=60, null=False, verbose_name="Name")
    EarliestTime = models.TimeField(auto_now=False, null=True, blank=True, verbose_name="Earliest Schedule Time")
    LatestTime = models.TimeField(auto_now=False, null=True, blank=True, verbose_name="Latest Schedule Time")
    OtherRules = models.TextField(null=True, blank=True, verbose_name="Other Rules")

    # def __iter__(self):
    #     return [self.Name,
    #             self.EarliestTime,
    #             self.LatestTime,
    #             self.OtherRules]

    class Meta:
        verbose_name_plural = "Chemotherapy Drugs"
        verbose_name = "Chemotherapy Drug"
