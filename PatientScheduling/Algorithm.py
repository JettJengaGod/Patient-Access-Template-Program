import os
from PatientScheduling.models import Appointment
from datetime import time
import UserSettings


# Function: convert_input
#
# Converts a time in the format HH:MM to a twople of hour,minute
#
# Parameters:
#
#    time - time in HH:MM format
#
# Returns:
#
#    twople of hour,minute


def convert_input(time):
    hour = int(time[0:2])
    minute = int(time[3:5])
    return hour, minute

start_time = UserSettings.get("DayStartDelay")/15
day_start = convert_input(UserSettings.get("OpenTime"))
num_chairs = UserSettings.get("MaxChairs")
day_close = convert_input(UserSettings.get("CloseTime"))
longest_time = (day_close[0]-day_start[0])*4+day_close[1]-day_start[1]


# Function: convert_to_format
#
# Converts a time in the format HH:MM to the format used in the algorithm.
#
#
# Parameters:
#
#     time - time in HH:MM formats
#
# Returns:
#
#     A single number representing how many 15 minute blocks the time is after the start of the day.
#
# See Also:
#
#     <convert_to_time>


def convert_to_format(time):
    if len(time) is 8:
        hour = int(time[0:2])
        hour -= day_start[0]
        minute = int(time[3:5])
        minute -= day_start[1]
        minute /= 15
        newTime = 4*hour +minute
    else:
        minute = int(time)
        minute /= 15
        newTime = minute
    return newTime


# Function: convert_to_time
#
# Converts a time from the format used in the algorithm to the format HH:MM.
#
# Parameters:
#
#    slots - A single number representing how many 15 minute blocks the time is after the start of the day.
#
# Returns:
#
#    A time in the format of HH:MM using the datetime libraries.
#
# See Also:
#
#    <convert_to_format>
#    <convert_to_duration>



def convert_to_time(slots):
    minutes = slots * 15
    hours = int(minutes/60)
    minutes -= hours*60
    hours += day_start[0]
    minutes += day_start[1]
    return time(hours, minutes)


# Function: convert_to_duration
#
# Converts a duration from the format used in the algorithm (slots) to the format HH:MM.
#
# Parameters:
#
#    slots - A single number representing how many 15 minute blocks long something is.
#
# Returns:
#
#    A string represnting a time in the format of "HH:MM".
#
# See Also:
#
#    <convert_to_format>
#    <convert_to_time>


def convert_to_duration(slots):
    minutes = slots * 15
    hours = int(minutes/60)
    minutes -= hours*60
    if hours == 0:
        return minutes
    if minutes == 0:
        return hours
    else:
        return str(hours) + ':' + str(minutes)

# Function: update_user_settings
#
# Updates the algorithm settings to the current ones in UserSettings
#
# See Also:
#
#    <convert_input>


def update_user_settings():
    start_time = UserSettings.get("DayStartDelay") / 15
    day_start = convert_input(UserSettings.get("OpenTime"))
    num_chairs = UserSettings.get("MaxChairs")
    day_close = convert_input(UserSettings.get("CloseTime"))
    longest_time = (day_close[0] - day_start[0]) * 4 + day_close[1] - day_start[1]

# Function: clean_input
#
# Takes the input from the forms on the page and converts it into something easy for the algortighm to work with
#
# Parameters:
#
#    nurseSchedules - a list of nurse schedule objects from the form
#    appointments - a list of appointment objects from the form
#    scheduled_appointments - a list of pre-reserved timeslots from the form
#
# Returns:
#
#    nurses - a list of nurses in the format of the algorithm with the prescheduled timeslots scheduled already
#    reserved_appointments - a list of appointments in the format of the form
#    appt - a list of appointments in the format of the algorithm
#
# See Also:
#
#    <convert_to_format>


def clean_input(nurseSchedules, appointments, scheduled_appointments):
    update_user_settings()
    # first we convert them to nurses
    nurses = []
    for nurse in nurseSchedules:
        nurses.append(Nurse(str(nurse.Team), convert_to_format(str(nurse.StartTime)),
                            convert_to_format(str(nurse.LunchTime)), convert_to_format(str(nurse.LunchDuration)),
                            convert_to_format(str(nurse.EndTime)), nurse.NurseID))
    nurses = sorted(nurses, key=lambda x: x.id)

    if scheduled_appointments[0].NurseScheduleID > -1:
        for appointment in scheduled_appointments:
            appointment.ChairID -= 1
            apptTime = convert_to_format(str(appointment.EndTime)) - convert_to_format(str(appointment.StartTime))
            if nurses[appointment.NurseScheduleID-1].end < convert_to_format(str(appointment.EndTime)):
                appointment.EndTime = convert_to_time(nurses[appointment.NurseScheduleID-1].end)
            if convert_to_format(str(appointment.StartTime)) > nurses[appointment.NurseScheduleID].end:
                scheduled_appointments.remove(appointment)
            else:
                nurses[appointment.NurseScheduleID-1].schedule(apptTime, 5, appointment.ChairID,convert_to_format(str(appointment.StartTime)))
        reserved_appointments = scheduled_appointments
    else:
        reserved_appointments = []
    # now we deal with the appointments
    appt = []
    for appointment in appointments:
        appt.extend(convert_to_format(str(appointment[0])) for x in range(int(str(appointment[1]))))
    return [nurses, reserved_appointments, appt]

# Function: run_algorithm
#
# Initilizes the nurses and runs the algorithm based on the input given
#
# Parameters:
#
#    nurses - a list of nurses in the format of the algorithm with the prescheduled timeslots scheduled already
#    appt - 2 lists of appointments in the format of the algorithm
#
# Returns:
#
#    final_appointments - a list of scheduled appointments in the format of the form
#    final_unscheduled - a list of appointments that were not able to be scheduled
#
# See Also:
#
#    <convert_to_time>
#    <schedule_slots>


def run_algorithm(nurses, appt):
    tempPod = [[nurses[0]]]  # first we seperate the nurses into pods
    for nurse in nurses:
        stored = False
        for i in range(len(tempPod)):
            if nurse.get_pod() == tempPod[i][0].get_pod():
                tempPod[i].append(nurse)
                stored = True
                break

        if stored is False:
            tempPod.append([nurse])
    pods = []    # making the nurses into pods
    for nurseGroup in tempPod:
        pods.append(Pod(nurseGroup))
    # now we send it into the scheduling algorithm
    end = []
    unscheduled = schedule_slots(pods, appt, end)
    final_unscheduled = []
    while len(unscheduled) > 0:
        tmp = unscheduled[0]
        final_unscheduled.append((convert_to_duration(tmp), unscheduled.count(tmp)))
        unscheduled = [x for x in unscheduled if x != tmp]

    # now we clean the output
    finalAppt = []
    for appointment in end:
        finalAppt.append(Appointment(NurseScheduleID=appointment.nurse.id,
                                     ChairID=appointment.chair,
                                     StartTime=convert_to_time(appointment.time),
                                     EndTime=convert_to_time(appointment.time + appointment.length)))

    return [finalAppt, final_unscheduled]

#    Class: Nurse
#
#    This class is used to hold the schedules and functions for individual nurses.
#
#
#    pod - the pod a nurse is in
#    start - the time the nurse starts
#    lunch - time the nurse's lunch starts
#    lunchlength - length of the nurse's lunch
#    end - time the nurse ends her day
#    identity - nurses ID number, used to differentiate between them
#    chairs - a 2d list of integers representing what is scheduled in each chair and time slot for a nurse
#       1 represents lunch
#       2 represents a point that has started an appointment in a different chair and no appointment scheduled
#       3 represents a point that has an appointment and has started an appointment in that time
#       4 represents a time before the start time of a nurse, after the end time or during a prereserved slot
#       5 and up represents an appointment going through that slot


class Nurse:
    def __init__(self,  pod, start, lunch, lunchlength,  end, identity):
        self.lunch = lunch
        self.lunchlength = lunchlength
        self.start = start
        self.end = end
        self.chairs = [[]]
        self.pod = pod
        self.id = identity
        self.populate()

    # Function: Nurse.help_start
    #
    #    Initialization function that fills the chairs based on the parameters handed in to the constructor
    #

    def populate(self):  # fills the list of chairs when a nurse is initialized
        self.chairs = [[0 for x in range(longest_time)] for x in range(num_chairs)]
        for i in range(num_chairs):
            for j in range(self.lunch, self.lunch + self.lunchlength):  # all lunch times are 1
                self.chairs[i][j] = 1
            for j in range(0, self.start):  # any time before starting is a 4
                self.chairs[i][j] = 4
            for j in range(0, start_time):  # any time before start_time is a 4
                self.chairs[i][j] = 4
            for j in range(self.end, longest_time):
                self.chairs[i][j] = 4

    def get_pod(self):
        return self.pod

    # Function: Nurse.__str__
    #
    #   A debug function that converts a description of the chairs to a string

    def __str__(self):  # function to print out which chairs are occupied by what at what times
        string = ""
        for j in range(self.end):
            for i in range(num_chairs-1):
                hour = 8 + j / 4
                minute = (j % 4) * 15
                string += str(hour) + ":" + str(minute)
                if minute is 0:
                    string += "0"
                string += "  "
                string += str(self.chairs[i][j]) + "  "
            string += "\n"
        return string
    # Function: Nurse.lunch_swap
    #
    #    Checks if a nurse can take over an appointment while another nurse is on lunch
    #
    #    # Parameters:
    #
    #    time - the number of slots since the beginning the other nurse's lunch starts
    #    length - how long the other nurse's lunch is
    #
    # Returns:
    #
    #    Boolean representing if this nurse can take the appointment or not
    #
    # See also:
    #    <check_other_nurses>

    def lunch_swap(self, time, length):
        for i in range(time, time + length):
            if self.chairs[num_chairs-1][i] > 0:
                return False
        return True

    # Function: Nurse.schedule
    #
    #    Schedules an appointment for a certain time. No collision detection done here that is done in <check_time>
    #
    #    Parameters:
    #
    #    appointment - the length of the appointment
    #    number - the number assigned to the appointment
    #    chair - which chair it is being scheduled in
    #    time - the time slot it begins at

    def schedule(self, appointment, number, chair, time):
        for i in range(time, time + appointment):
            self.chairs[chair][i] = number
        for i in range(num_chairs):
            if self.chairs[i][time] >= 3:  # if there is an appointment
                self.chairs[i][time] = 3
            else:
                self.chairs[i][time] = 2
            if self.chairs[i][time+1] >= 3:
                self.chairs[i][time+1] = 3
            else:
                self.chairs[i][time+1] = 2

    # Function: Nurse.help_start
    #
    #    Called when a nurse helps another nurse in the pod start the appointment, it sets the times when they are
    #    helping to 2s or 3s depending on the circumstance.
    #
    #    # Parameters:
    #
    #    time - the time slot it begins at
    def help_start(self, time):  # sets the helper nurses starting time to 2s and 3s
        for i in range(num_chairs-1):
            if self.chairs[i][time] >= 3:
                self.chairs[i][time] = 3
            else:
                self.chairs[i][time] = 2
            if self.chairs[i][time+1] >= 3:
                self.chairs[i][time+1] = 3
            else:
                self.chairs[i][time+1] = 2

# Class: Pod
#    Contains multiple nurses and functions pertaining to the scheduling of appointments


class Pod:
    def __init__(self, nurses):
        self.nurses = nurses

    def __str__(self):
        str = ""
        for nurse in self.nurses:
            str += nurse.__str__()
        return str
    # Function: morning_schedule
    #   Loops through a pod to see if it can schedule a single appointment
    #   Time -> Nurse -> Chairs
    # Parameters:
    #
    #    length - how long the appointment is
    #    appt_number - the number attached to the appointment
    #
    # Returns:
    #
    #    An object of the type <Alg_Appointment> if there is an available slot in the pod open or false if there is not
    #
    # See Also:
    #    <Alg_Appointment> <check_time>

    def morning_schedule(self, length, appt_number):
        for k in range(0, longest_time):
            for j in range(num_chairs-1):
                for i in range(len(self.nurses)):
                    check = self.check_time(i, j, k, length, appt_number)
                    if check:
                        return check
        return False

    # Function: evening_schedule
    #   Loops through a pod to see if it can schedule a single appointment in the evening
    #   Time -> Nurse -> Chairs
    # Parameters:
    #
    #    length - how long the appointment is
    #    appt_number - the number attached to the appointment
    #
    # Returns:
    #
    #    An object of the type <Alg_Appointment> if there is an available slot in the pod open or false if there is not
    #
    # See Also:
    #    <Alg_Appointment> <check_time>

    def evening_schedule(self, length, appt_number):
        for k in range(longest_time-1, 0, -1):
            for j in range(num_chairs - 1):
                for i in range(len(self.nurses)):
                    check = self.check_time(i, j, k-length, length, appt_number)
                    if check:
                        return check
        return False

    # Function: check_time
    #   Checks to see if a specific time on a nurse is open to be scheduled
    # Parameters:
    #
    #    nurseindex - the index of the nurse in the current pod
    #    chair - the index of the chair we are checking
    #    time - the timeslot of the first part of the appointment we are checking
    #    length - how long the appointment is
    #    appt_number - the number attached to the appointment
    #
    # Returns:
    #
    #    An object of the type <Alg_Appointment> if this appointment can be scheduled here false if it cannot
    #
    # See Also:
    #    <Alg_Appointment> <single_schedule> <check_other_nurses>

    def check_time(self, nurseindex, chair, time, length, appt_number):
        current = self.nurses[nurseindex]
        if time+length >= longest_time:  # it goes past the nurse's end time
            return False
        for i in range(0, length):
            if current.chairs[chair][time + i] > 2:  # any point in the middle is already scheduled with an appointment
                return False
        if current.chairs[chair][time + length] is 1 or current.chairs[chair][time + length + 1] is 1 or current.chairs[chair][time + length - 1] is 1:  # ends during lunch
            return False
        extra = -1
        if current.chairs[chair][time] is 1 or current.chairs[chair][time-1] is 1 or current.chairs[chair][time+1] is 1:  # starts during lunch
            return False
        if current.chairs[chair][time] > 0 or current.chairs[chair][time+1] > 0:  # needs help starting the appointment
            for i in range(len(self.nurses)):
                for j in range(num_chairs-1):
                    if self.nurses[i].chairs[j][time] not in[1, 2, 3, 4]and self.nurses[i].chairs[j][time - 1] not in[1, 2, 3, 4] and self.nurses[i].chairs[j][time + 1] not in[1, 2, 3, 4] and extra is -1 and i is not nurseindex:
                        extra = [i, j]  # the index of the nurse that can help
                        break
            if extra is -1:  # found no one to help
                return False
        for i in range(2, length):
            if current.chairs[chair][time + i] is 1:  # appt goes through lunch
                lunch = self.check_other_nurses(current, appt_number)  # checks to see if other nurses can cover
                if not lunch:
                    return False
                break
        appt = Alg_Appointment(length, current, chair, time, appt_number)  # initializes the Alg_Appointment object
        if extra is not -1:  # needed help starting
            self.nurses[extra[0]].help_start(time)  # properly sets the other nurse's chair values
        current.schedule(length, appt_number, chair, time)  # schedules the appointment for this nurse
        return appt

    # Function: check_other_nurses
    #   Checks the other nurses in the pod to see if they can take over during lunch and schedules them if they can
    #
    # Parameters:
    #
    #    nurse - the index of the nurse in the current pod
    #    appt_number - the number attached to the appointment
    #
    # Returns:
    #
    #    True if another nurse can take it False if they cant
    #
    # See Also:
    #
    #    <lunch_swap> <check_time>

    def check_other_nurses(self, nurse, appt_number):
        found = -1
        for i in range(len(self.nurses)):
            if self.nurses[i].lunch_swap(nurse.lunch, nurse.lunchlength)and self.nurses[i] is not nurse:
                found = i
                break
        if found is not -1:
            lunch = self.nurses[found]
            for i in range(nurse.lunch, nurse.lunch + nurse.lunchlength):
                lunch.chairs[num_chairs-1][i] = appt_number
            return True
        return False

# Class: Alg_Appointment
#    Class that is used to return to the web page


class Alg_Appointment:
    def __init__(self, length, nurse, chair, time, appt):
        self.length = length
        self.nurse = nurse
        self.chair = chair
        self.time = time
        self.number = appt

    def __str__(self):
        string = ""
        string += "id " + str(self.nurse.id) + " length " + str(self.length) + " number " + str(self.number)
        return string


# Function: schedule_slots
#   Schedules the list of appointments sent in from the webpage and returns a list of appointments it couldn't schedule
#
# Parameters:
#
#    pods - list of pods that have been supplied from the webpage
#    appointments - 2 lists of appointments that need to be scheduled in the format of how long they are
#    final - the list of scheduled appointments that is handed back to the webpage
#
# Returns:
#
#    discarded - a list of appointments that could not be scheduled
#    final - a list of scheduled <Alg_Appointments>


def schedule_slots(pods, appointments, final):
    number = 5
    discarded = []
    appointments = sorting_hat(appointments, 19, 8)
    while len(appointments) is not 0:
        stuck = number + 0
        for i in range(len(pods)):
            if len(appointments) is 0:
                break
            a = pods[i].morning_schedule(appointments[0], number)
            if a:
                print a
                appointments.pop(0)
                final.append(a)
                number += 1
        if number is stuck and len(appointments) is not 0:
            discarded.append(appointments.pop(0))
            # return "Failed"
    final.sort(key=lambda x: (x.nurse.id, x.chair, x.time))
    return discarded


def sorting_hat(l,high,low):
    l = sorted(l)
    l.reverse()
    highlist = []
    lowlist = []
    while l[0] > high:
        highlist.append(l.pop(0))
    l = sorted(l)
    while l[1] < low and len(l) > 1:
        highlist.append(l.pop(0))
        lowlist.append(l.pop(0))
    highlist += l
    l = highlist
    l+=(lowlist)
    return l