from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.validators import RegexValidator
from django.forms import formset_factory, ModelForm
from django.utils.datetime_safe import datetime

from PatientScheduling import UserSettings
from PatientScheduling.models import NurseSchedule


class CompanyForm(forms.Form):
    MaxChairs=forms.IntegerField(label="Chairs per RN", min_value=1, max_value=10, required=True)
    OpenTime=forms.TimeField(label="Open Time", required=True)
    CloseTime=forms.TimeField(label="Close Time", required=True)
    DayStartDelay=forms.IntegerField(label="Start Delay", min_value=0, required=True)
    AppointmentStagger=forms.IntegerField(label="Appointment Stagger", min_value=0, required=True)

    def clean(self):
        cleaned_data = super(CompanyForm, self).clean()
        OpenTime = cleaned_data.get("OpenTime")
        CloseTime = cleaned_data.get("CloseTime")
        try:
            if OpenTime > CloseTime:
                raise forms.ValidationError('The open time must be before the close time')
        except:
            return # allow the django alert to pop up


class RNForm(ModelForm):

    class Meta:
        model = NurseSchedule
        fields = ['StartTime', 'LunchTime', 'LunchDuration', 'EndTime', 'Team']
        error_messages = {
            NON_FIELD_ERRORS: {
                'Team': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }

    # TODO fix try | except
    def clean(self):
        error_messages = []
        # try:
        cleaned_data = super(RNForm, self).clean()
        Team = cleaned_data.get("Team")
        StartTime = cleaned_data.get("StartTime")
        LunchTime = cleaned_data.get("LunchTime")
        LunchDuration = cleaned_data.get("LunchDuration")
        EndTime = cleaned_data.get("EndTime")

        OpenTime = datetime.time(datetime.strptime(UserSettings.get("OpenTime"),"%H:%M"))
        CloseTime = datetime.time(datetime.strptime(UserSettings.get("CloseTime"),"%H:%M"))

        # does not conform to DRY principle?
        if not Team or not StartTime or not EndTime:
            raise forms.ValidationError('Please fill out all of the fields')
        if StartTime >= EndTime:
            error_messages.append('RNs cannot start after EndTime')
        if StartTime < OpenTime:
            error_messages.append('A RN can not start before the company opens at ' + OpenTime.strftime("%I:%M"))
        if EndTime > CloseTime:
            error_messages.append('A RN must leave before the company closes at ' + CloseTime.strftime("%I:%M"))
        if not LunchTime or (LunchTime and (LunchTime < StartTime or LunchTime > EndTime)):
            error_messages.append('RNs need a valid lunch start time')
        if len(error_messages):
            raise forms.ValidationError(' & '.join(error_messages))
        return self.cleaned_data
        # except:
            # raise forms.ValidationError('RNForm clean function error')


RNFormSet = formset_factory(RNForm, min_num=3, can_delete=True)


class AppointmentForm(forms.Form):
    TIMESLOTS = (
       (30, '30 Minutes'),
       (45, '45 Minutes'),
       (60, '1 Hour'),
       (90, '1 Hour 30 Minutes'),
       (120, '2 Hours'),
       (150, '2 Hours 30 Minutes'),
       (180, '3 Hours'),
       (210, '3 Hours 30 Minutes'),
       (240, '4 Hours'),
       (270, '4 Hours 30 Minutes'),
       (300, '5 Hours'),
       (330, '5 Hours 30 Minutes'),
       (360, '6 Hours'),
       (390, '6 Hours 30 Minutes'),
       (420, '7 Hours'),
       (450, '7 Hours 30 Minutes'),
       (480, '8 Hours'),
        )
    TimeOfDay = forms.ChoiceField(label='Preferred Time', choices=(('M', 'Morning'), ('A', 'Afternoon')), initial='M')
    TimePeriod = forms.ChoiceField(label='Time Period', choices=TIMESLOTS)
    Amount = forms.IntegerField(label='Amount',
                                initial=1,
                                min_value=0,
                                max_value=99)


AppointmentFormSet = formset_factory(AppointmentForm, can_delete=True)


class ReservedForm(forms.Form):
    StartTime = forms.TimeField(label='Start Time', required=False)
    EndTime = forms.TimeField(label='End Time', required=False)
    RNNumber = forms.IntegerField(label='RN Number', min_value=0, required=False)
    ChairNumber = forms.ChoiceField(label='Chair Number', required=False,
                                    choices=[(str(n),int(n)) for n in range(1, UserSettings.get("MaxChairs")+1)])
    def clean(self):
        cleaned_data = super(ReservedForm, self).clean()
        StartTime = cleaned_data.get("StartTime")
        EndTime = cleaned_data.get("EndTime")
        RNNumber = cleaned_data.get("EndTime")
        try:
            if StartTime > EndTime:
                raise forms.ValidationError('The start time must be before the end time')
            if RNNumber != None and (StartTime == None or EndTime == None):
                raise forms.ValidationError('Please complete all fields')
        except:
            return # allow the django alert to pop up


ReservedFormSet = formset_factory(ReservedForm, can_delete=True)