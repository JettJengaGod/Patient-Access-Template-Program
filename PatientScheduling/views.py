from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, ChairsForm, StartEndForm, CompanyForm
from PatientScheduling.models import NurseSchedule, MinMaxTime
from PatientScheduling.Algorithm import clean_input

# remove comment below to allow admin only access to this view
@user_passes_test(lambda u: u.is_staff)
def my_admin_only_view(request):
    startend_form = StartEndForm()
    # startend_form = CompanyForm()
    context = {'StartEndForm': startend_form}
    return render(request, 'settings.html', context)


def new_schedule(request):
    global idNumber
    idNumber = 0
    chairs_form = ChairsForm()
    startend_form = StartEndForm()
    rn_form = RNFormSet(prefix='RN')
    app_form = AppointmentFormSet(prefix='APP')
    context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form, 'StartEndForm': startend_form}

    if request.method == 'POST':  # if this is a POST request we need to process the form data
        minmaxTime = MinMaxTime.objects.get(id=01)
        chairs_form = ChairsForm(request.POST)
        rn_form = RNFormSet(request.POST, prefix='RN')
        app_form = AppointmentFormSet(request.POST, prefix='APP')
        startend_form = StartEndForm(request.POST)
        if rn_form.is_valid() & app_form.is_valid() & chairs_form.is_valid() & startend_form.is_valid():
            chairs = range(chairs_form.cleaned_data.get('NumberOfChairs'))
            ctemp = chairs_form.cleaned_data.get('NumberOfChairs') + 1
            nurses = []
            NurseNumber = 1
            startTime = minmaxTime.MinTime
            endTime = minmaxTime.MaxTime
            # startTime = startend_form.cleaned_data.get('workStart')
            # endTime = startend_form.cleaned_data.get('workEnd')
            for form in rn_form:
                cd = form.cleaned_data
                nurses.append(NurseSchedule(
                    NurseID=NurseNumber,
                    Team=cd.get('Team'),
                    StartTime=cd.get('StartTime'),
                    LunchTime=cd.get('LunchTime'),
                    LunchDuration=cd.get('LunchDuration'),
                    EndTime=cd.get('EndTime'),
                ))
                NurseNumber += 1
            needed_appointments = []
            for form in app_form:
                cd = form.cleaned_data
                needed_appointments.append([cd.get('TimePeriod'), cd.get('Amount')])
            all_appointments = clean_input(nurses, needed_appointments)  # this starts the algorithm
            scheduled_appointments = all_appointments[0]
            unscheduled_appointments = all_appointments[1]
            nurses = sorted(nurses, key=lambda x: x.Team)  # sort by team for easier viewing
            context = {
                'RNSet': nurses,
                'Chairs': chairs,
                'Appointments': scheduled_appointments,
                'RNSize': ctemp,
                'UnschAppts' : unscheduled_appointments,
                'startTime' : startTime,
                'endTime' : endTime
            }
            # data = serializers.serialize("xml", startend_form)
            # print data
            # save to the session in case user saves calendar later
            # request.session['nurseSchedules'] = serializers.serialize('json', nurses)
            # request.session['appointments'] = serializers.serialize('json', scheduled_appointments)
            return render(request, 'calendar.html', context)
        else:
            context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form, 'StartEndForm': startend_form}
    return render(request, 'new_schedule.html', context)


def generate_schedule(request):
    return render(request, 'calendar.html')


def home(request):
    return render(request, 'home.html')