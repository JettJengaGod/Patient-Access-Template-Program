from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, ChairsForm
from PatientScheduling.models import NurseSchedule


def new_schedule(request):
    if request.method == 'POST':  # if this is a POST request we need to process the form data
        chairs_form = ChairsForm(request.POST)
        rn_form = RNFormSet(request.POST, prefix='RN')
        app_form = AppointmentFormSet(request.POST, prefix='APP')
        if rn_form.is_valid() & app_form.is_valid() & chairs_form.is_valid():
            chairs = chairs_form.cleaned_data.get('NumberOfChairs')
            nurses = []
            for form in rn_form:
                cd = form.cleaned_data
                nurses.append(NurseSchedule(
                    StartTime=cd.get('StartTime'),
                    LunchTime=cd.get('LunchTime'),
                    LunchDuration=cd.get('LunchDuration'),
                    EndTime=cd.get('EndTime')
                ))
            appointments = []
            for form in app_form:
                cd = form.cleaned_data
                appointments.append([cd.get('TimePeriod'), cd.get('Amount')])
            context = {'RNSet': nurses, 'Chairs': chairs, 'Appointments': appointments}
            return render(request, 'generate_schedule.html', context)
    else:  # if a GET (or any other method) we'll create a blank form
        chairs_form = ChairsForm()
        rn_form = RNFormSet(prefix='RN')
        app_form = AppointmentFormSet(prefix='APP')
    context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form}
    return render(request, 'new_schedule.html', context)


def generate_schedule(request):
    return render(request, 'generate_schedule.html')
