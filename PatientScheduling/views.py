from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, ChairsForm
from PatientScheduling.models import NurseSchedule
from PatientScheduling.Algorithm import clean_input


def new_schedule(request):
    global idNumber
    idNumber = 0
    chairs_form = ChairsForm()
    rn_form = RNFormSet(prefix='RN')
    app_form = AppointmentFormSet(prefix='APP')
    context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form}

    if request.method == 'POST':  # if this is a POST request we need to process the form data
        chairs_form = ChairsForm(request.POST)
        rn_form = RNFormSet(request.POST, prefix='RN')
        app_form = AppointmentFormSet(request.POST, prefix='APP')
        if rn_form.is_valid() & app_form.is_valid() & chairs_form.is_valid():
            chairs = range(chairs_form.cleaned_data.get('NumberOfChairs'))
            ctemp = chairs_form.cleaned_data.get('NumberOfChairs') + 1
            nurses = []
            NurseNumber = 1
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
            # TODO: Add to below context 'UnscheduledAppointments': UnscheduledAppointments
            # ScheduledAppointments must be sorted by nurse, by chair, and by time (earliest first)
            # assuming the following names are in the AppointmentClass: StartTime, EndTime, ChairID, NurseScheduleID
            context = {'RNSet': sorted(nurses, key=lambda x: x.Team), 'Chairs': chairs, 'Appointments': scheduled_appointments, 'RNSize': ctemp, 'UnschAppts' : unscheduled_appointments}
            return render(request, 'calendar.html', context)
        else:
            context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form}
    return render(request, 'new_schedule.html', context)


def generate_schedule(request):
    return render(request, 'calendar.html')


def home(request):
    return render(request, 'home.html')