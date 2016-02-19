from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import formset_factory, ModelForm

from PatientScheduling.models import NurseSchedule


class ChairsForm(forms.Form):
    NumberOfChairs = forms.IntegerField(
            label='Number of Available Chairs',
            required=True,
            initial=0,
            min_value=0,
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
        StartTime = cleaned_data.get("StartTime")
        LunchTime = cleaned_data.get("LunchTime")
        LunchDuration = cleaned_data.get("LunchDuration")
        EndTime = cleaned_data.get("EndTime")

        # does not conform to DRY principle?
        if not StartTime or not LunchTime or not LunchDuration or not EndTime:
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
       (10, '10 Minutes'),
       (20, '20 Minutes'),
       (30, '30 Minutes'),
        )
    TimePeriod = forms.ChoiceField(label='Time Period', choices=TIMESLOTS)
    Amount = forms.IntegerField(label='Amount',
                                initial=0,
                                min_value=0,
                                max_value=99
                                )


AppointmentFormSet = formset_factory(AppointmentForm, can_delete=True)

