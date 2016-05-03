from operator import attrgetter

import time

from datetime import datetime
import yaml
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from PatientScheduling import UserSettings
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, CompanyForm, ReservedFormSet
from PatientScheduling.models import NurseSchedule, SavedSchedule, Appointment, ChemotherapyDrug
from PatientScheduling.Algorithm import clean_input


def new_schedule(request):
    chairs = UserSettings.get("MaxChairs")
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
                    ChairID=int(cd.get('ChairNumber'))
                ))
            # -----Run Algorithm and build the context----- #
            all_appointments = clean_input(nurses, needed_appointments, reserved_appointments)  # this starts the algorithm
            scheduled_appointments = sorted(all_appointments[0], key=attrgetter('NurseScheduleID','ChairID','StartTime'))
            unscheduled_appointments = all_appointments[1]
            reserved_appointments = all_appointments[2]
            maxtime = max(nurses, key=attrgetter('EndTime')).EndTime
            if maxtime.minute == 0:
                maxhour = maxtime.hour - 1
            else:
                maxhour = maxtime.hour
            mintime = min(nurses, key=attrgetter('StartTime')).StartTime
            context = {'RNSet': nurses, 'RNSize': chairs+1, 'Appointments': scheduled_appointments, 'Chairs': range(0, chairs),
                       'UnschAppts': unscheduled_appointments, 'reserved_appointments': reserved_appointments,
                       'Drugs': ChemotherapyDrug.objects.all(),
                       'DayDuration': getHourRange(mintime, maxtime), 'closeTime': maxhour}
            # -----save to the session in case user saves calendar later----- #
            request.session['nurseSchedules'] = serializers.serialize('json', nurses)
            request.session['appointments'] = serializers.serialize('json', scheduled_appointments)
            return render(request, 'calendar.html', context)
        # end if form is valid
        context = {'RNFormSet': rn_form, 'Chairs': range(0, chairs), 'AppointmentFormSet': app_form, 'ReservedFormSet': reserved_form}
        return render(request, 'new_schedule.html', context)
    else:  # not post
        rn_form = RNFormSet(prefix='RN')
        app_form = AppointmentFormSet(prefix='APP')
        reserved_form = ReservedFormSet(prefix='RESERVED')
        context = {'RNFormSet': rn_form, 'Chairs': range(0, chairs), 'AppointmentFormSet': app_form, 'ReservedFormSet': reserved_form}
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
        chairs = nurse_group.Chairs
        maxtime = max(nurses, key=attrgetter('EndTime'))
        if maxtime.minute == 0:
            maxhour = maxtime.hour - 1
        else:
            maxhour = maxtime.hour
        mintime = min(nurses, key=attrgetter('StartTime'))
        context = {'Schedule': schedule, 'RNSet': nurses, 'Chairs': range(0,chairs), 'Appointments': appointments,
                   'RNSize': chairs+1, 'Drugs': ChemotherapyDrug.objects.all(),
                   'DayDuration': getHourRange(mintime, maxtime), 'closeTime': maxhour}
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


def getHourRange(mintime, maxtime):
    if maxtime.minute == 0:
        maxtime = maxtime.hour - 1
    else:
        maxtime = maxtime.hour
    mintime = mintime.hour
    if maxtime <= 12:
        return range(mintime, maxtime+1)
    else:
        maxtime = maxtime - 12
    if mintime > 12:
        mintime = mintime - 12
        return range(mintime, maxtime)

    morning = range(mintime, 13)
    evening = range(1, maxtime+1)
    return morning + evening