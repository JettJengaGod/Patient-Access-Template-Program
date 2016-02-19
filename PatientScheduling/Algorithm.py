def set_elements(array, rowStart, rowEnd, colStart, colEnd, assignment):
    for i in xrange(rowStart, rowEnd, 1):
        for j in xrange(colStart, colEnd, 1):
            array[i][j] = assignment


def insert_slot(length, array, chair, numNurse):
    nurseCol = numNurse * 3  # looks cleaner this way
    for i in array:
        if i == 2:
            continue
        elif 2 in array[i:i + length, numNurse * 3 + chair]:
            continue
        else:  # schedule slot and mark the other chairs
            array[i:i + length, nurseCol + chair] = 2
            if chair == 0:
                array[i:i + 2, nurseCol + 1] = 2  # beginings
                array[i:i + 2, nurseCol + 2] = 2
                array[i + length - 2:i + length, nurseCol + 1] = 2  # ends
                array[i + length - 2:i + length, nurseCol + 2] = 2
            if chair == 1:
                array[i:i + 2, nurseCol + chair - 1] = 2  # beginings
                array[i:i + 2, nurseCol + chair + 1] = 2
                array[i + length - 2:i + length, nurseCol] = 2  # ends
                array[i + length - 2:i + length, nurseCol + 2] = 2
            if chair == 2:
                array[i:i + 2, nurseCol] = 2  # beginings
                array[i:i + 2, nurseCol + 1] = 2
                array[i + length - 2:i + length, nurseCol] = 2  # ends
                array[i + length - 2:i + length, nurseCol + 1] = 2
                return True
    return False


def schedule_slots2(slots, nurses):
    # nurse input is (nurse id, lunch time, start time, end time)
    # slots input is (length, #)
    # this is assuming our input is in military time
    schedule = [[0 for x in range(3 * len(nurses))] for x in range(37)]
    # schedule nurse lunches and absence periods
    i = 0
    for (nurse_id, lunch, start, end) in nurses:
        set_elements(schedule, lunch, lunch + 4, i * 3, i * 3 + 3,
                     1)  # 1 denotes a lunch break, which can be scheduled for
        if start != 0:
            set_elements(schedule, 0, start, i * 3, i * 3 + 3,
                         2)  # 2 denotes either a scheduled slot or that they are not at the hospital
        if end != 37:
            set_elements(schedule, end + 1, 37, i * 3, i * 3 + 3, 2)
        i += 1
        # print schedule
        # now to schedule the slots
        # while slots != Null	#while we still have slots left


#
#	for(length, quantity) in slots: #for every slot
#		Empty = False
#		for chair in xrange(3):	#for every chair
#			for nurse in xrange(len(nurses)): #for every nurse
#				if quantity ==0:
#					break
#				inserted = insert_slot(length,schedule, chair, nurse)
#				if inserted == True:
#					quantity-=1


class Nurse:
    def __init__(self, lunch, lunchlength, start, end):
        self.lunch = lunch
        self.lunchlength = lunchlength
        self.start = start
        self.end = end
        self.chairs = [[]]
        self.populate()

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

    def populate(self):  # fills the list of chairs when a nurse is initialized
        self.chairs = [[0 for x in range(self.end)] for x in range(4)]
        for i in range(4):
            for j in range(self.lunch, self.lunch + self.lunchlength):  # all lunch times are 1
                self.chairs[i][j] = 1
            for j in range(0, self.start):  # any time before starting is a 3
                self.chairs[i][j] = 3

    def schedule(self, appointment, number, chair, time):  # fills the schedule with an appointment
        for i in range(time, time + appointment):
            self.chairs[chair][i] = number
        for i in range(3):
            if i is not chair:
                self.chairs[i][time] = max(2, self.chairs[i][time])
                self.chairs[i][time + 1] = max(2, self.chairs[i][time + 1])
                if appointment is 3:
                    self.chairs[i][time + 2] = max(2, self.chairs[i][time + 2])
                elif appointment > 3:
                    self.chairs[i][time + appointment - 2] = max(2, self.chairs[i][time + appointment - 2])
                    self.chairs[i][time + appointment - 1] = max(2, self.chairs[i][time + appointment - 1])

    def avaliblity(self, appointment, nurses, index):  # returns first avalible appointment or false if not avlalible
        for i in range(3):
            for j in range(self.start, self.end - appointment + 1):
                check_time = self.check_time(appointment, i, j)
                if check_time is "lunch":
                    other_index = self.check_other_nurses(nurses, self.lunch, index)
                    if other_index:
                        return [i, j, other_index - 1]
                elif check_time:
                    return [i, j]
        return False

    def check_time(self, appointment, chair, time):  # Checks ifa time works for an appointment or if it is during lunch
        if self.chairs[chair][time] > 0 or self.chairs[chair][time] > 0:
            return False
        for i in range(2, appointment):
            if self.chairs[chair][time + i] > 2:
                return False
        if self.chairs[chair][time + appointment - 2] > 0 or self.chairs[chair][time + appointment - 1] > 0:
            return False
        for i in range(2, appointment):
            if self.chairs[chair][time + i] is 1:
                return "lunch"
        return True

    def check_other_nurses(self, nurses, time, index):
        for i in range(len(nurses)):
            if i is not index:
                if nurses[i].check_time(self.lunchlength, 3, time):
                    return i + 1
        return False


def schedule_slots(nurses, appointments):
    assert len(appointments) is not 0
    number = 4
    discarded = []
    while len(appointments) is not 0:
        stuck = number + 0
        for i in range(len(nurses)):
            if len(appointments) is 0:
                return
            a = nurses[i].avaliblity(appointments[0], nurses, i)
            if a is not False:
                nurses[i].schedule(appointments[0], number, a[0], a[1])
                if len(a) is 3:  # This appointment goes through lunch
                    nurses[a[2]].schedule(nurses[i].lunchlength, number, 3, nurses[i].lunch)
                appointments.pop(0)
                number += 1
        if number is stuck:
            discarded.append(appointments.pop(0))
            # return "Failed"
    return discarded


appt = []
appt.extend(28 for x in range(3))
appt.extend(24 for x in range(3))
appt.extend(22 for x in range(2))
appt.extend(20 for x in range(5))
appt.extend(18 for x in range(2))
appt.extend(16 for x in range(8))
appt.extend(14 for x in range(2))
appt.extend(12 for x in range(12))
appt.extend(10 for x in range(10))
appt.extend(8 for x in range(9))
appt.extend(6 for x in range(29))
appt.extend(4 for x in range(20))
appt.extend(3 for x in range(8))
appt.extend(2 for x in range(23))

Nurses = [Nurse(10, 4, 0, 33) for x in range(4)]
Nurses.extend(Nurse(14, 4, 4, 39) for x in range(4))
Nurses.extend(Nurse(18, 4, 0, 33) for x in range(4))
appointments = [5, 7, 4, 4, 4, 4, 4, 4, 4, 4, 4]
print(schedule_slots(Nurses, appt))
for l in range(len(Nurses)):
    print "Nurse " + str(l + 1)
    print Nurses[l]
