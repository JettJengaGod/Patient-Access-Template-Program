import json
import string, random

from django.db import transaction
from django.http import HttpResponse
from django.core import serializers

from PatientScheduling import UserSettings
from PatientScheduling.models import NurseScheduleGroups, NurseSchedule, SavedSchedule, Appointment, SavedTimeSlot


def generate_key(size):
    chars=string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))

# ------used to load/manage nurses and nurse schedules------- #


def check_schedule_group_name(request):
    name = request.GET['ScheduleGroupName']
    try:
        NurseScheduleGroups.objects.get(Name=name, UserCreated=True)
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse('True', content_type="application/json")  # unique Schedule Name
    else:
        return HttpResponse('False', content_type="application/json")  # unique Schedule Name


def load_schedule_group_names(request):
    try:
        nameslist = NurseScheduleGroups.objects.filter(UserCreated=True)
        jsonstring = "[]"
        if len(nameslist) > 0:
            jsonstring = serializers.serialize('json', nameslist)
        return HttpResponse(jsonstring, content_type="application/json")
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")


def delete_schedule_group(request):
    name = request.GET['ScheduleGroupName']
    try:
        NurseScheduleGroups.objects.get(Name=name).delete()
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse('failed to delete ' + name, content_type="application/json")
    return HttpResponse('removed all ' + name + ' schedules', content_type="application/json")


def add_to_schedule_group(request):
    r = request.GET
    group_name = r['ScheduleGroupName']
    try:  # check if the name has already been used
        group_object = NurseScheduleGroups.objects.get(Name=group_name, UserCreated=True)
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        # if the name has already been used add the nurse to the group
        group_object = NurseScheduleGroups(Name=group_name, UserCreated=True, Chairs=UserSettings.get("MaxChairs"))
        group_object.save()
    rn = NurseSchedule(
        Team=r['Team'],
        ScheduleGroupName=group_object,
        StartTime=r['StartTime'],
        LunchTime=r['LunchTime'],
        LunchDuration=r['LunchDuration'],
        EndTime=r['EndTime']
    )
    rn.save()
    return HttpResponse('The rn schedule ' + group_name + 'has been saved', content_type="application/json")


def load_schedule_group(request):
    name = request.GET['ScheduleGroupName']
    try:
        rnlist = NurseSchedule.objects.filter(ScheduleGroupName=name)
        return HttpResponse(serializers.serialize('json', rnlist), content_type="application/json")
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")

# -------used to load/manage appointment duration input------ #


def load_time_slot_group_names(request):
    try:
        nameslist = SavedTimeSlot.objects.filter()      # what do I put for a parameter here****************
        jsonstring = "[]"
        if len(nameslist) > 0:
            jsonstring = serializers.serialize('json', nameslist)
        return HttpResponse(jsonstring, content_type="application/json")
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")



def load_time_slot_group(request):
    name = request.GET['SaveName']
    try:
        time_slot_list = SavedTimeSlot.objects.filter(Name=name)
        return HttpResponse(serializers.serialize('json', time_slot_list), content_type="application/json")
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")


def save_time_slot(request):
    save_name = request.GET['SaveName']
    duration = request.GET['Duration']
    count = request.GET['Count']
    time_slot = SavedTimeSlot(Name=save_name, Duration=duration, Count=count)
    time_slot.save()
    return HttpResponse('The duration and number of the time slots: ' + save_name + 'has been saved', content_type="application/json")


def delete_time_slot(request):
    name = request.GET['SaveName']
    try:
        SavedTimeSlot.objects.get(Name=name).delete()
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse('failed to delete ' + name, content_type="application/json")
    return HttpResponse('removed all ' + name + ' schedules', content_type="application/json")


def check_time_slot_group_name(request):
    name = request.GET['SaveName']


    # ---- duration = request.GET['Duration']
    #count = request.GET['NumTimeSlots']
    try:
        SavedTimeSlot.objects.filter(Name=name)
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse('True', content_type="application/json")  # unique Time Slot Name
    else:
        return HttpResponse('False', content_type="application/json")  # unique Time Slot Name


# ------used to load/manage full schedules------- #

@transaction.atomic  # ensures that either all of the DB changes are saved or none
def save_schedule(request):
    save_name = request.GET['SaveName']
    # Save the nurse schedules
    nurse_group = NurseScheduleGroups(Name=generate_key(20), UserCreated=False, Chairs=UserSettings.get("MaxChairs"))
    nurse_group.save()
    for wrapper in serializers.deserialize('json', request.session.get('nurseSchedules')):
        wrapper.object.ScheduleGroupName = nurse_group
        wrapper.object.save()
    # Save the schedule object that links nurses and appointments
    schedule = SavedSchedule(Name=save_name, NurseSchedule=nurse_group)
    schedule.save()
    # Save the appointments
    for wrapper in serializers.deserialize('json', request.session.get('appointments')):
        wrapper.object.SavedSchedule = schedule
        wrapper.object.save()
    return HttpResponse('The schedule ' + save_name + ' has been saved', content_type="application/json")


@transaction.atomic  # ensures that either all of the DB changes are saved or none
def remove_schedule(request):
    save_name = request.GET['SaveName']
    try:
        schedule = SavedSchedule.objects.get(Name=save_name)
        nurse_group = schedule.NurseSchedule
        nurses = NurseSchedule.objects.filter(ScheduleGroupName=nurse_group)
        appointments = Appointment.objects.filter(SavedSchedule=schedule)
        schedule.delete()
        nurse_group.delete()
        nurses.delete()
        appointments.delete()
    except():
        return HttpResponse('An error has occurred', content_type="application/json")
    return HttpResponse('Deleted ' + save_name, content_type="application/json")


def load_schedule(request):
    save_name = request.GET['SaveName']
    try:
        schedule = SavedSchedule.objects.get(Name=save_name)
        nurse_group = schedule.NurseSchedule
        nurses = NurseSchedule.objects.filter(ScheduleGroupName=nurse_group)
        appointments = Appointment.objects.filter(SavedSchedule=schedule)
        return HttpResponse(serializers.serialize('json', [nurses, appointments]), content_type="application/json")
    except():
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")


def check_schedule_name(request):
    name = request.GET['SaveName']
    try:
        SavedSchedule.objects.get(Name=name)
    except (KeyError, SavedSchedule.DoesNotExist):
        return HttpResponse('False', content_type="application/json")  # unique Schedule Name
    else:
        return HttpResponse('True', content_type="application/json")

