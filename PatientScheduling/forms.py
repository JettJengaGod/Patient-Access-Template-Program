from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.validators import RegexValidator
from django.forms import formset_factory, ModelForm

from PatientScheduling.models import NurseSchedule


class ChairsForm(forms.Form):
    NumberOfChairs = forms.IntegerField(
            label='Max Number of Chairs per RN',
            required=True,
            initial=4,
            min_value=1,
            max_value=99
    )


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

        # does not conform to DRY principle?
        if not Team or not StartTime or not LunchTime or not LunchDuration or not EndTime:
            raise forms.ValidationError('Please fill out all of the fields')
        if StartTime >= EndTime:
            error_messages.append('RNs cannot start after EndTime')
        if LunchDuration == 0:
            error_messages.append('RNs need a lunch break')
        if LunchTime < StartTime or LunchTime > EndTime:
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
    TimePeriod = forms.ChoiceField(label='Time Period', choices=TIMESLOTS)
    Amount = forms.IntegerField(label='Amount',
                                initial=1,
                                min_value=0,
                                max_value=99
                                )


AppointmentFormSet = formset_factory(AppointmentForm, can_delete=True)


class ReservedForm(forms.Form):
    StartTime = forms.TimeField(label='Start Time')
    EndTime = forms.TimeField(label='End Time')
    RNNumber = forms.IntegerField(label='RN Number', min_value=0)

ReservedFormSet = formset_factory(ReservedForm, can_delete=True)