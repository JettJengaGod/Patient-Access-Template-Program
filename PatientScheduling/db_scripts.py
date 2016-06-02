import json
import string, random
from operator import attrgetter

from django.db import transaction
from django.http import HttpResponse
from django.core import serializers

from PatientScheduling import UserSettings
from PatientScheduling.models import NurseScheduleGroups, NurseSchedule, SavedSchedule, Appointment, SavedTimeSlot, \
    SavedTimeSlotGroup, ChemotherapyDrug

'''
   Function: generate_key

      Generates a random string of ascii characters with length 'size'.
      Used to create a random save name for RNSchedules when saving a generated appointment schedule

   Parameters:

      size - length of characters

   Returns:

      The randomly generated string
'''
def generate_key(size):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))

# ------used to load/manage nurses and nurse schedules------- #
'''
   Function: check_schedule_group_name

      Checks if a RN schedule with the given name exists in the DB

   Parameters:

      request.GET['ScheduleGroupName'] - The save name to be checked

   Returns:

      True - If the provided name is unique
      False - If the provided name has been used already
'''
def check_schedule_group_name(request):
    name = request.GET['ScheduleGroupName']
    try:
        NurseScheduleGroups.objects.get(Name=name, UserCreated=True)
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse('True', content_type="application/json")  # unique Schedule Name
    else:
        return HttpResponse('False', content_type="application/json")  # unique Schedule Name

'''
   Function: load_schedule_group_names

      Attempts to load a list of existing RN schedules from the DB

   Parameters:

      None

   Returns:

      A json serialized list of all saved RN schedules


'''
def load_schedule_group_names(request):
    try:
        nameslist = NurseScheduleGroups.objects.filter(UserCreated=True)
        jsonstring = "[]"
        if len(nameslist) > 0:
            jsonstring = serializers.serialize('json', nameslist)
        return HttpResponse(jsonstring, content_type="application/json")
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")

'''
   Function: delete_schedule_group

      Attempts to remove the RN schedule with the given save name from the DB.

   Parameters:

      request.GET['ScheduleGroupName'] - The save name of the RN schedule to be deleted

   Returns:

      A HttpResponse with either a success or fail message
'''
def delete_schedule_group(request):
    name = request.GET['ScheduleGroupName']
    try:
        NurseScheduleGroups.objects.get(Name=name).delete()
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse('failed to delete ' + name, content_type="application/json")
    return HttpResponse('removed all ' + name + ' schedules', content_type="application/json")

'''
   Function: add_to_schedule_group

      Adds a RN to the RN schedule. If the given RN schedule does not exist, one is created.

   Parameters:

      request.GET['ScheduleGroupName'] - the name of the RN schedule
      request.GET['Team'] - the pod this particular RN is in
      request.GET['StartTime'] - the time this particular RN starts work
      request.GET['LunchTime'] - the time the RN leaves for lunch
      request.GET['LunchDuration'] - the duration of the lunch break
      request.GET['EndTime'] - the time this particular RN ends work

   Returns:

      A HttpResponse with either a success or fail message

    See Also:
        <UserSettings.get>

'''
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

'''
   Function: load_schedule_group

      Attempts to load the RN schedule with the given name from the DB

   Parameters:

      request.GET['ScheduleGroupName'] - the name of the RN schedule

   Returns:

      A json serialized string containing a list of all loaded RN objects from the DB
'''
def load_schedule_group(request):
    name = request.GET['ScheduleGroupName']
    try:
        rnlist = NurseSchedule.objects.filter(ScheduleGroupName=name)
        return HttpResponse(serializers.serialize('json', rnlist), content_type="application/json")
    except (KeyError, NurseScheduleGroups.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")

# -------used to load/manage appointment duration input------ #

'''
   Function: load_time_slot_group_names

      Loads the save name of all currently saved time slot inputs

   Parameters:

      None

   Returns:

      A Json serialized list of saved names
'''
def load_time_slot_group_names(request):
    try:
        groups = SavedTimeSlotGroup.objects.all()
        jsonstring = "[]"
        if len(groups) > 0:
            jsonstring = serializers.serialize('json', groups)
        return HttpResponse(jsonstring, content_type="application/json")
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")

'''
   Function: load_time_slot_group

      Attempts to load the time slot input with the given saved name from the DB

   Parameters:

      request.GET['SaveName']

   Returns:

      A json serialized string of saved names
'''
def load_time_slot_group(request):
    name = request.GET['SaveName']
    try:
        group_object = SavedTimeSlotGroup.objects.get(Name=name)
        time_slot_list = SavedTimeSlot.objects.filter(Group=group_object)
        time_slot_list = sorted(time_slot_list, key=attrgetter('Priority'))
        return HttpResponse(serializers.serialize('json', time_slot_list), content_type="application/json")
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")

'''
   Function: save_time_slot

      Adds the given time slot to the input group in the DB with the given name.
      If the input group does not exist in the DB, then one is created.

   Parameters:

      request.GET['SaveName'] - the name of the saved time slot group
      request.GET['Duration'] - the duration of the given time slot
      request.GET['Count'] - how many time slots are requested
      request.GET['Priority'] - the scheduling priority of the time slot
      request.GET['TimeOfDay'] - either M (morning) or E (evening) preferred schedule time

   Returns:

      A HttpResponse with either a success or fail message
'''
def save_time_slot(request):
    save_name = request.GET['SaveName']
    try:  # check if the name has already been used
        group_object = SavedTimeSlotGroup.objects.get(pk=save_name)
    except (KeyError, SavedTimeSlotGroup.DoesNotExist):
        # if the name has already been used add the nurse to the group
        group_object = SavedTimeSlotGroup(pk=save_name)
        group_object.save()
    duration = request.GET['Duration']
    priority = request.GET['Priority']
    count = request.GET['Count']
    time_of_day = request.GET['TimeOfDay']
    time_slot = SavedTimeSlot(Group=group_object, Duration=duration, Count=count, Priority=priority, TimeOfDay=time_of_day)
    time_slot.save()
    return HttpResponse('The duration and number of the time slots: ' + save_name + 'has been saved', content_type="application/json")

'''
   Function: delete_time_slot

      Attempts to remove the saved time slot group with the matching primary key from the DB

   Parameters:

      request.GET['SaveName'] - the name of the time slot input group to be delted

   Returns:

      A HttpResponse with either a success or fail message
'''
def delete_time_slot(request):
    save_name = request.GET['SaveName']
    try:
        SavedTimeSlotGroup.objects.get(Name=save_name).delete()
    except (KeyError, SavedTimeSlot.DoesNotExist):
        return HttpResponse('failed to delete ' + save_name, content_type="application/json")
    return HttpResponse('removed all ' + save_name + ' schedules', content_type="application/json")

'''
   Function: check_time_slot_group_name

      Searches the DB to see if the given name has already been used for a time slot group save name

   Parameters:

      request.GET['SaveName'] - the name to be checked

   Returns:

      false - if the given name is unique
      true - if the given name has already been used
'''
def check_time_slot_group_name(request):
    save_name = request.GET['SaveName']
    try:
        SavedTimeSlotGroup.objects.get(Name=save_name)
    except (KeyError, SavedTimeSlotGroup.DoesNotExist):
        return HttpResponse('False', content_type="application/json")  # unique Time Slot Name
    else:
        return HttpResponse('True', content_type="application/json")


# ------used to load/manage full schedules------- #
'''
   Function: save_schedule

      Grabs the input used to generate the schedule from the session variables 'nurseSchedules' and 'appointments'
      and saves them to the DB along with the generated appointments

   Parameters:

      request.GET['SaveName'] - the save name to be used

   Returns:

      A HttpResponse with either a success or fail message

   See Also:
        <UserSettings.get>
'''
@transaction.atomic  # ensures that either all of the DB changes are saved or none
def save_schedule(request):
    # todo: check if the session is still valid
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

'''
   Function: remove_schedule

      Attempts to remove the schedule with the matching name from the DB and all associated foreign key objects
      from the DB

   Parameters:

      request.GET['SaveName'] - the save name of the schedule

   Returns:

      A HttpResponse with either a success or fail message
'''
@transaction.atomic  # ensures that either all of the DB changes are saved or none
def remove_schedule(request):
    save_name = request.GET['SaveName']
    try:
        schedule = SavedSchedule.objects.get(Name=save_name)
        nurse_group = schedule.NurseSchedule
        appointments = Appointment.objects.filter(SavedSchedule=schedule)
        nurses = NurseSchedule.objects.filter(ScheduleGroupName=nurse_group)
        nurse_group.delete()
        nurses.delete()
        appointments.delete()
        schedule.delete()
    except():
        return HttpResponse('An error has occurred', content_type="application/json")
    return HttpResponse('Deleted ' + save_name, content_type="application/json")

'''
   Function: check_schedule_name

      Checks if the given name has been used to save another schedule already

   Parameters:

      request.GET['SaveName'] - the save name to check

   Returns:

      false - if the schedule name is unique
      true - if the name has been used
'''
def check_schedule_name(request):
    name = request.GET['SaveName']
    try:
        SavedSchedule.objects.get(Name=name)
    except (KeyError, SavedSchedule.DoesNotExist):
        return HttpResponse('False', content_type="application/json")  # unique Schedule Name
    else:
        return HttpResponse('True', content_type="application/json")

# ------------ used to load an chemotherapy drug --------- #

'''
   Function: load_chemotherapy_drug

      Loads the chemotherapy drug object from the DB that has the associated name

   Parameters:

      request.GET['Name'] - the drug name

   Returns:

      A json serialized object representing the drug
'''
def load_chemotherapy_drug(request):
    name = request.GET['Name']

    try:
        DrugObject = ChemotherapyDrug.objects.filter(Name=name)
        return HttpResponse(serializers.serialize('json', DrugObject), content_type="application/json")
    except (KeyError, ChemotherapyDrug.DoesNotExist):
        return HttpResponse(serializers.serialize('json', []), content_type="application/json")