from operator import attrgetter, itemgetter

import time

from datetime import datetime
import yaml
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from PatientScheduling import UserSettings
from PatientScheduling.forms import RNFormSet, AppointmentFormSet, CompanyForm, ReservedFormSet, AppointmentForm
from PatientScheduling.models import NurseSchedule, SavedSchedule, Appointment, ChemotherapyDrug
from PatientScheduling.Algorithm import clean_input, run_algorithm

@login_required
def new_schedule(request):
    chairs = UserSettings.get("MaxChairs")
    if request.method == 'POST':  # if this is a POST request we need to process the form data
        rn_form = RNFormSet(request.POST, prefix='RN')
        app_form = AppointmentFormSet(request.POST, prefix='APP')
        reserved_form = ReservedFormSet(request.POST, prefix='RESERVED')
        prioritize_longest = len(request.POST.getlist('PrioritizeLongest')) > 0
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
                needed_appointments.append([int(cd.get('TimePeriod')), int(cd.get('Amount'))])
            needed_appointments = sorted(needed_appointments, key=itemgetter(0), reverse=True)
            # -----Build list of pre-reserved time slots----- #
            reserved_appointments = []
            for form in reserved_form:
                cd = form.cleaned_data
                app = Appointment(
                    StartTime=cd.get('StartTime'),
                    EndTime=cd.get('EndTime'),
                    NurseScheduleID=cd.get('RNNumber'),
                    ChairID=int(cd.get('ChairNumber'))
                )
                setattr(app, 'reserved', True)
                reserved_appointments.append(app)
            # -----Run Algorithm and build the context----- #
            cleaned_input = clean_input(nurses, needed_appointments, reserved_appointments)  # clean the input
            all_appointments = run_algorithm(cleaned_input[0], cleaned_input[2])
            scheduled_appointments = all_appointments[0] + cleaned_input[1]
            scheduled_appointments = sorted(scheduled_appointments, key=attrgetter('NurseScheduleID', 'ChairID', 'StartTime'))
            unscheduled_appointments = all_appointments[1]
            maxtime = max(nurses, key=attrgetter('EndTime')).EndTime
            if maxtime.minute == 0:
                maxhour = maxtime.hour - 1
            else:
                maxhour = maxtime.hour
            mintime = min(nurses, key=attrgetter('StartTime')).StartTime
            context = {'RNSet': nurses, 'RNSize': chairs+1, 'Appointments': scheduled_appointments, 'Chairs': range(0, chairs),
                       'UnschAppts': unscheduled_appointments,
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
        appointment = AppointmentForm()
        appt_minutes = []
        for x,y in appointment.TIMESLOTS:
            appt_minutes.append(x)
        reserved_form = ReservedFormSet(prefix='RESERVED')
        context = {'RNFormSet': rn_form, 'Chairs': range(0, chairs), 'AppointmentFormSet': app_form, 'ReservedFormSet': reserved_form, 'appt_ts': appt_minutes}
        return render(request, 'new_schedule.html', context)

@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def saved_schedules(request):
    saved = SavedSchedule.objects.order_by('-SavedDate')
    context = {'saved_list': saved}
    return render(request, 'viewsavedschedule.html', context)


@login_required
def view_schedule(request, schedule_id):
    schedule = get_object_or_404(SavedSchedule, pk=schedule_id)
    try:
        nurse_group = schedule.NurseSchedule
        nurses = NurseSchedule.objects.filter(ScheduleGroupName=nurse_group)
        nurses = sorted(nurses, key=attrgetter('Team', 'NurseID'))
        appointments = Appointment.objects.filter(SavedSchedule=schedule)
        appointments = sorted(appointments, key=attrgetter('NurseScheduleID', 'ChairID', 'StartTime'))
        chairs = nurse_group.Chairs
        maxtime = max(nurses, key=attrgetter('EndTime')).EndTime
        if maxtime.minute == 0:
            maxhour = maxtime.hour - 1
        else:
            maxhour = maxtime.hour
        mintime = min(nurses, key=attrgetter('StartTime')).StartTime
        context = {'Schedule': schedule, 'RNSet': nurses, 'Chairs': range(0, chairs), 'Appointments': appointments,
                   'RNSize': chairs+1, 'Drugs': ChemotherapyDrug.objects.all(),
                   'DayDuration': getHourRange(mintime, maxtime), 'closeTime': maxhour}
        return render(request, 'calendar.html', context)
    except:
        raise Http404("Unable to load schedule '" + schedule.Name + "'")

@login_required
def settings_page(request):
    company_form = CompanyForm()
    save_bool = False
    if request.method != 'POST':
        sett = UserSettings.getAll()
        if sett:
            company_form = CompanyForm\
                (initial={
                    'MaxChairs': int(sett["MaxChairs"]),
                    'OpenTime': sett["OpenTime"],
                    'CloseTime': sett["CloseTime"],
                    'DayStartDelay': sett["DayStartDelay"],
                    'AppointmentStagger': sett["AppointmentStagger"]
                }) # set: {'name': val}
    else: # if this is a POST request we need to process the form data
        company_form = CompanyForm(request.POST)
        if company_form.is_valid():
            cd = company_form.cleaned_data
            settings = {
                    'MaxChairs': cd.get("MaxChairs"),
                    'OpenTime': cd.get("OpenTime").strftime("%H:%M"),
                    'CloseTime': cd.get("CloseTime").strftime("%H:%M"),
                    'DayStartDelay': cd.get("DayStartDelay"),
                    'AppointmentStagger': cd.get("AppointmentStagger")
                }
            UserSettings.saveAll(settings)
            save_bool = True
            # return render(request, 'home.html')
    context = {'CompanyForm': company_form, 'save_bool': save_bool}
    return render(request, 'settings_page.html', context)


def guide(request):
    return render(request, 'documentation.html')


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