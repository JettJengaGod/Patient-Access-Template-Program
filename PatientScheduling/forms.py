from django import forms
from django.forms import formset_factory


class ChairsForm(forms.Form):
    NumberOfChairs = forms.IntegerField(label='Number of Available Chairs')


class RNForm(forms.Form):
    StartTime = forms.TimeField(label='Start Time')
    LunchTime = forms.TimeField(label='Lunch Time')
    LunchDuration = forms.IntegerField(label='Lunch Duration')
    EndTime = forms.TimeField(label='End Time')
    ID = int


RNFormSet = formset_factory(RNForm, min_num=3)


class AppointmentForm(forms.Form):
    TIMESLOTS = (
       (10, '10 Minutes'),
       (20, '20 Minutes'),
       (30, '30 Minutes'),
        )
    TimePeriod = forms.ChoiceField(label='Time Period', choices=TIMESLOTS)
    Amount = forms.IntegerField(label='Amount', initial=0)


AppointmentFormSet = formset_factory(AppointmentForm)

