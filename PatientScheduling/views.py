from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, ChairsForm
from PatientScheduling.models import NurseSchedule


def new_schedule(request):
    chairs_form = ChairsForm()
    rn_form = RNFormSet(prefix='RN')
    app_form = AppointmentFormSet(prefix='APP')
    context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form}

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
                    Team=cd.get('Team'),
                    StartTime=cd.get('StartTime'),
                    LunchTime=cd.get('LunchTime'),
                    LunchDuration=cd.get('LunchDuration'),
                    EndTime=cd.get('EndTime'),
                ))
            appointments = []
            for form in app_form:
                cd = form.cleaned_data
                appointments.append([cd.get('TimePeriod'), cd.get('Amount')])
            context = {'RNSet': sorted(nurses, key=lambda x: x.Team), 'Chairs': chairs, 'Appointments': appointments}
            return render(request, 'calendar.html', context)
        else:
            context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form, 'GroupCount': group_count}
    return render(request, 'new_schedule.html', context)


def generate_schedule(request):
    return render(request, 'calendar.html')
