import json
from django.http import HttpResponse
from django.core import serializers
from PatientScheduling.models import NurseScheduleGroups, NurseSchedule


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
        nameslist = NurseScheduleGroups.objects.get(UserCreated=True)
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
    try:
        group_object = NurseScheduleGroups.objects.get(Name=group_name)
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        group_object = NurseScheduleGroups(Name=group_name)
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


