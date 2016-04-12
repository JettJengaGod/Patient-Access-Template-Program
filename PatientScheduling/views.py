from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, ChairsForm
from PatientScheduling.models import NurseSchedule, SavedSchedule, Appointment
from PatientScheduling.Algorithm import clean_input


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
            chairs = range(chairs_form.cleaned_data.get('NumberOfChairs'))
            ctemp = chairs_form.cleaned_data.get('NumberOfChairs') + 1
            nurses = []
            for form in rn_form:
                cd = form.cleaned_data
                nurses.append(NurseSchedule(
                    NurseID=0,
                    Team=cd.get('Team'),
                    StartTime=cd.get('StartTime'),
                    LunchTime=cd.get('LunchTime'),
                    LunchDuration=cd.get('LunchDuration'),
                    EndTime=cd.get('EndTime'),
                ))
            needed_appointments = []
            for form in app_form:
                cd = form.cleaned_data
                needed_appointments.append([cd.get('TimePeriod'), cd.get('Amount')])
            nurses = sorted(nurses, key=lambda x: x.Team)  # sort by team for easier viewing
            for i in range(1, len(nurses)+1):
                nurses[i-1].NurseID = i
            all_appointments = clean_input(nurses, needed_appointments)  # this starts the algorithm
            scheduled_appointments = all_appointments[0]
            unscheduled_appointments = all_appointments[1]
            nurses = sorted(nurses, key=lambda x: x.Team)  # sort by team for easier viewing
            context = {'RNSet': nurses, 'Chairs': chairs, 'Appointments': scheduled_appointments, 'RNSize': ctemp, 'UnschAppts' : unscheduled_appointments}
            # save to the session in case user saves calendar later
            # request.session['nurseSchedules'] = serializers.serialize('json', nurses)
            # request.session['appointments'] = serializers.serialize('json', scheduled_appointments)
            return render(request, 'calendar.html', context)
        else:
            context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ChairsForm': chairs_form}
    return render(request, 'new_schedule.html', context)


def generate_schedule(request):
    return render(request, 'calendar.html')


def home(request):
    return render(request, 'home.html')


def saved_schedules(request):
    saved = SavedSchedule.objects.order_by('-SavedDate')
    context = {'saved_list': saved}
    return render(request, 'viewsavedschedule.html', context)


def view_schedule(request, schedule_id):
    schedule = get_object_or_404(SavedSchedule, pk=schedule_id)
    try:
        nurse_group = schedule.NurseSchedule
        nurses = NurseSchedule.objects.filter(ScheduleGroupName=nurse_group)
        appointments = Appointment.objects.filter(SavedSchedule=schedule)
        chairs = range(4)
        # ToDo: change the way we ask the user for the number of chairs per nurse and have it be accessible here
        ctemp = 4 + 1
        context = {'Schedule': schedule, 'RNSet': nurses, 'Chairs': chairs, 'Appointments': appointments, 'RNSize': ctemp}
        return render(request, 'calendar.html', context)
    except:
        raise Http404("Unable to load schedule '" + schedule.Name + "'")
