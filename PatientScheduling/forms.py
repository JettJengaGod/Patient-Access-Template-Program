from django import forms
from django.forms import formset_factory, ModelForm

from PatientScheduling.models import NurseSchedule


class ChairsForm(forms.Form):
    NumberOfChairs = forms.IntegerField(label='Number of Available Chairs')


class RNForm(ModelForm):
    class Meta:
        model = NurseSchedule
        fields = ['StartTime', 'LunchTime', 'LunchDuration', 'EndTime']


RNFormSet = formset_factory(RNForm, min_num=3, can_delete=True)


class AppointmentForm(forms.Form):
    TIMESLOTS = (
       (10, '10 Minutes'),
       (20, '20 Minutes'),
       (30, '30 Minutes'),
        )
    TimePeriod = forms.ChoiceField(label='Time Period', choices=TIMESLOTS)
    Amount = forms.IntegerField(label='Amount', initial=0)


AppointmentFormSet = formset_factory(AppointmentForm, can_delete=True)

