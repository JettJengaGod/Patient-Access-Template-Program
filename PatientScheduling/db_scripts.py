import json
from django.http import HttpResponse
from django.core import serializers
from PatientScheduling.models import ScheduleGroups, NurseSchedule


def check_schedule_group_name(request):
    name = request.GET['ScheduleGroupName']
    try:
        ScheduleGroups.objects.get(Name=name)
    except (KeyError, ScheduleGroups.DoesNotExist):
        return HttpResponse('True', content_type="application/json")  # unique Schedule Name
    else:
        return HttpResponse('False', content_type="application/json")  # unique Schedule Name


def load_schedule_group_names(request):
    nameslist = ScheduleGroups.objects.all()
    jsonstring = serializers.serialize('json', nameslist)
    return HttpResponse(jsonstring, content_type="application/json")


def delete_schedule_group(request):
    name = request.GET['ScheduleGroupName']
    try:
        ScheduleGroups.objects.get(Name=name).delete()
    except (KeyError, ScheduleGroups.DoesNotExist):
        return
    return


def add_to_schedule_group(request):
    r = request.GET
    group_name = r['ScheduleGroupName']
    try:
        group_object = ScheduleGroups.objects.get(Name=group_name)
    except (KeyError, ScheduleGroups.DoesNotExist):
        group_object = ScheduleGroups(Name=group_name)
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
    rnlist = NurseSchedule.objects.filter(ScheduleGroupName=name)
    jsonstring = serializers.serialize('json', rnlist)
    return HttpResponse(jsonstring, content_type="application/json")

