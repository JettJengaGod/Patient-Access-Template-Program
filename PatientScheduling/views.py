from operator import attrgetter

import time
import yaml
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from PatientScheduling import UserSettings
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, CompanyForm, ReservedFormSet
from PatientScheduling.models import NurseSchedule, SavedSchedule, Appointment
from PatientScheduling.Algorithm import clean_input


def new_schedule(request):
    if request.method == 'POST':  # if this is a POST request we need to process the form data
        rn_form = RNFormSet(request.POST, prefix='RN')
        app_form = AppointmentFormSet(request.POST, prefix='APP')
        reserved_form = ReservedFormSet(request.POST, prefix='RESERVED')
        if rn_form.is_valid() & app_form.is_valid() & reserved_form.is_valid():
            # -----Build nurse objects---- #
            nurses = []
            for form in rn_form:
                cd = form.cleaned_data
                nurses.append(NurseSchedule(
                    NurseID=0,
                    Team=cd.get('Team'),
                    StartTime=cd.get('StartTime'),
                    LunchTime=cd.get('LunchTime'),
                    LunchDuration=cd.get('LunchDuration'),
                    EndTime=cd.get('EndTime')
                ))
            nurses = sorted(nurses, key=lambda x: x.Team)  # sort by team for easier viewing
            for i in range(1, len(nurses)+1):
                nurses[i-1].NurseID = i
            # -----Build list of needed time slots----- #
            needed_appointments = []
            for form in app_form:
                cd = form.cleaned_data
                needed_appointments.append([cd.get('TimePeriod'), cd.get('Amount')])
            # -----Build list of pre-reserved time slots----- #
            reserved_appointments = []
            for form in reserved_form:
                cd = form.cleaned_data
                reserved_appointments.append(Appointment(
                    StartTime=cd.get('StartTime'),
                    EndTime=cd.get('EndTime'),
                    NurseScheduleID=cd.get('RNNumber'),
                    ChairID=cd.get('ChairNumber')
                ))
            # -----Run Algorithm and build the context----- #
            all_appointments = clean_input(nurses, needed_appointments, reserved_appointments)  # this starts the algorithm
            scheduled_appointments = sorted(all_appointments[0], key=attrgetter('NurseScheduleID','ChairID','StartTime'))
            unscheduled_appointments = all_appointments[1]
            reserved_appointments = all_appointments[2]
            chairs = UserSettings.get("MaxChairs")
            context = {'RNSet': nurses, 'Chairs': range(1,chairs+1), 'Appointments': scheduled_appointments,
                       'RNSize': chairs+1, 'UnschAppts': unscheduled_appointments, 'reserved_appointments': reserved_appointments}
            # -----save to the session in case user saves calendar later----- #
            request.session['nurseSchedules'] = serializers.serialize('json', nurses)
            request.session['appointments'] = serializers.serialize('json', scheduled_appointments)
            return render(request, 'calendar.html', context)
        # end if form is valid
        context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ReservedFormSet': reserved_form}
        return render(request, 'new_schedule.html', context)
    else:  # not post
        rn_form = RNFormSet(prefix='RN')
        app_form = AppointmentFormSet(prefix='APP')
        reserved_form = ReservedFormSet(prefix='RESERVED')
        context = {'RNFormSet': rn_form, 'AppointmentFormSet': app_form, 'ReservedFormSet': reserved_form}
        return render(request, 'new_schedule.html', context)


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


def settings_page(request):
    company_form = CompanyForm()
    if request.method != 'POST':
        with open('UserSettings', 'r') as f:
            set = yaml.load(f)
        if set:
            company_form = CompanyForm\
                (initial={
                    'MaxChairs': set["MaxChairs"],
                    'OpenTime': set["OpenTime"],
                    'CloseTime': set["CloseTime"],
                    'DayStartDelay': set["DayStartDelay"],
                    'AppointmentStagger': set["AppointmentStagger"]
                }) # set: {'name': val}
    else: # if this is a POST request we need to process the form data
        company_form = CompanyForm(request.POST)
        if company_form.is_valid():
            cd = company_form.cleaned_data
            with open('UserSettings', 'w') as f:
                settings = {
                    'MaxChairs': cd.get("MaxChairs"),
                    'OpenTime': cd.get("OpenTime").strftime("%H:%M"),
                    'CloseTime': cd.get("CloseTime").strftime("%H:%M"),
                    'DayStartDelay': cd.get("DayStartDelay"),
                    'AppointmentStagger': cd.get("AppointmentStagger")
                }
                yaml.dump(settings, f)
                return render(request, 'home.html')
    context = {'CompanyForm': company_form}
    return render(request, 'settings_page.html', context)