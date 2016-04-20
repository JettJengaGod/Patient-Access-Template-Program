
from PatientScheduling.models import NurseSchedule
from PatientScheduling.models import Appointment
import math
from datetime import datetime
from datetime import time
longest_time = 40
start_time = 1


def convert_to_format(time):
    if len(time) is 8:
        hour = int(time[0:2])
        hour -= 8
        minute = int(time[3:5])
        minute /= 15
        newTime = 4*hour +minute
    else:
        minute = int(time)
        minute /= 15
        newTime = minute
    return newTime


def convert_to_time(slots):
    minutes = slots * 15
    hours = int(minutes/60)
    minutes -= hours*60
    hours += 8
    return time(hours,minutes)


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


def clean_input(nurseSchedules, appointments, scheduled_appointments):
    # first we convert them to nurses
    nurses = []
    for nurse in nurseSchedules:
        nurses.append(Nurse(str(nurse.Team), convert_to_format(str(nurse.StartTime)),
                            convert_to_format(str(nurse.LunchTime)), convert_to_format(str(nurse.LunchDuration)),
                            convert_to_format(str(nurse.EndTime)), nurse.NurseID))

    # then we deal with the pods
    nurses = sorted(nurses, key=lambda x: x.id)
    tempPod = [[nurses[0]]] #first we seperate the nurses into pods
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

    # now we deal with the appointments
    appt = []
    for appointment in appointments:
        appt.extend(convert_to_format(str(appointment[0])) for x in range(int(str(appointment[1]))))

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

    return [finalAppt, final_unscheduled, reserved_appointments]


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

    def get_pod(self):
        return self.pod

    def __str__(self):  # function to print out which chairs are occupied by what at what times
        string = ""
        for j in range(self.end):
            for i in range(3):
                hour = 8 + j / 4
                minute = (j % 4) * 15
                string += str(hour) + ":" + str(minute)
                if minute is 0:
                    string += "0"
                string += "  "
                string += str(self.chairs[i][j]) + "  "
            string += "\n"
        return string

    def lunch_swap(self, time, length):
        for i in range(time, time + length):
            if self.chairs[3][i] > 0:
                return False
        return True

    def schedule(self, appointment, number, chair, time):  # fills the schedule with an appointment
        for i in range(time, time + appointment):
            self.chairs[chair][i] = number
        for i in range(4):
            if self.chairs[i][time] >= 3:
                self.chairs[i][time] = 3
            else:
                self.chairs[i][time] = 2
            if self.chairs[i][time+1] >= 3:
                self.chairs[i][time+1] = 3
            else:
                self.chairs[i][time+1] = 2

    def help_start(self, time):
        for i in range(3):
            if self.chairs[i][time] >= 3:
                self.chairs[i][time] = 3
            else:
                self.chairs[i][time] = 2
            if self.chairs[i][time+1] >= 3:
                self.chairs[i][time+1] = 3
            else:
                self.chairs[i][time+1] = 2

    def populate(self):  # fills the list of chairs when a nurse is initialized
        self.chairs = [[0 for x in range(longest_time)] for x in range(4)]
        for i in range(4):
            for j in range(self.lunch, self.lunch + self.lunchlength):  # all lunch times are 1
                self.chairs[i][j] = 1
            for j in range(0, self.start):  # any time before starting is a 4
                self.chairs[i][j] = 4
            for j in range(0, start_time):  # any time before start_time is a 4
                self.chairs[i][j] = 4
            for j in range(self.end, longest_time):
                self.chairs[i][j] = 4


class Pod:
    def __init__(self, nurses):
        self.nurses = nurses

    def __str__(self):
        str = ""
        for nurse in self.nurses:
            str += nurse.__str__()
        return str

    def single_schedule(self, length, appt_number):
        for k in range(0, longest_time):
            for j in range(3):
                for i in range(len(self.nurses)):
                    check = self.check_time(i, j, k, length, appt_number)
                    if check:
                        return check
        return False

    def check_time(self, nurseindex, chair, time, length, appt_number):
        current = self.nurses[nurseindex]
        if time+length >= longest_time:
            return False
        for i in range(0, length):
            if current.chairs[chair][time + i] > 2:
                return False
        if current.chairs[chair][time + length] is 1 or current.chairs[chair][time + length - 1] is 1:
            return False
        extra = -1
        if current.chairs[chair][time] is 1 or current.chairs[chair][time+1] is 1:
            return False
        if current.chairs[chair][time] > 0 or current.chairs[chair][time+1] > 0:
            for i in range(len(self.nurses)):
                for j in range(3):
                    if self.nurses[i].chairs[j][time] not in[1, 2, 3, 4] and self.nurses[i].chairs[j][time + 1] not in[1, 2, 3, 4] and extra is -1 and i is not nurseindex:
                        extra = [i, j]
                        break
            if extra is -1:
                return False
        for i in range(2, length):
            if current.chairs[chair][time + i] is 1:
                lunch = self.check_other_nurses(current, appt_number)
                if not lunch:
                    return False
                break
        appt = Alg_Appointment(length, current, chair, time, appt_number)
        if extra is not -1:
            self.nurses[extra[0]].help_start(time)
        current.schedule(length, appt_number, chair, time)
        return appt

    def check_other_nurses(self, nurse, appt_number):
        found = -1
        for i in range(len(self.nurses)):
            if self.nurses[i].lunch_swap(nurse.lunch, nurse.lunchlength)and self.nurses[i] is not nurse:
                found = i
                break
        if found is not -1:
            lunch = self.nurses[found]
            for i in range(nurse.lunch, nurse.lunch + nurse.lunchlength):
                lunch.chairs[3][i] = appt_number
            return True
        return False


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


def schedule_slots(pods, appointments, final):
    appointments.sort()
    appointments.reverse()
    number = 5
    discarded = []
    while len(appointments) is not 0:
        stuck = number + 0
        for i in range(len(pods)):
            if len(appointments) is 0:
                return discarded
            a = pods[i].single_schedule(appointments[0], number)
            if a:
                print a
                appointments.pop(0)
                final.append(a)
                number += 1
        if number is stuck:
            discarded.append(appointments.pop(0))
            # return "Failed"
    final.sort(key=lambda x: (x.nurse.id, x.chair, x.time))
    return discarded
#
# lunch, lunchlength, start, end, pod, identity
# appt = []
# appt.extend(28 for x in range(3))
# appt.extend(24 for x in range(3))
# appt.extend(22 for x in range(2))
# appt.extend(20 for x in range(5))
# appt.extend(18 for x in range(2))
# appt.extend(16 for x in range(8))
# appt.extend(14 for x in range(2))
# appt.extend(12 for x in range(12))
# appt.extend(10 for x in range(10))
# appt.extend(8 for x in range(40))
# appt.extend(6 for x in range(29))
# appt.extend(4 for x in range(20))
# appt.extend(3 for x in range(8))
# appt.extend(2 for x in range(23))
# pods = [Pod([Nurse(10+x, 4, 0, 33, 1, x) for x in range(4)]), Pod([Nurse(14+x, 4, 4, 39, 2, x+4) for x in range(4)]), \
#         Pod([Nurse(18+x, 4, 0, 33, 3, x+8) for x in range(4)])]
# pods = [Pod([Nurse(1, 0, 12, 4, 32, 1), Nurse(1, 0, 16, 4, 32, 1), Nurse(1, 0, 20, 4, 32, 1), Nurse(1, 0, 24, 4, 32, 1)])]
# end = []
# print(schedule_slots(pods, appt, end))
# for pod in pods:
#     print pod
#
