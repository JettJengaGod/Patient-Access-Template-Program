class Nurse:
    def __init__(self, lunch, lunchlength, start, end, pod, identity):
        self.lunch = lunch
        self.lunchlength = lunchlength
        self.start = start
        self.end = end
        self.chairs = [[]]
        self.populate()
        self.pod = pod
        self.id = identity


class Pod:
    def __init__(self, nurses):
        self.nurses = nurses

    def check_avlilbility(self, length):
        for i in range(len(self.nurses)):
            for j in range(3):
                for k in range(self.nurses[j].start, self.nurses[j].end-length+1):
                    check = self.check_time(i, j, k, length)
            # for i in range(3):
            # for j in range(self.start, self.end - appointment + 1):
            #     check_time = self.check_time(nurses, appointment, i, j)
            #     if check_time is "lunch":
            #         other_index = self.check_other_nurses(nurses, self.lunch, index)
            #         if other_index:
            #             return [i, j, other_index - 1]
            #     elif check_time:
            #         return [i, j]

    def check_time(self, nurseindex, chair, time, length):
        current = self.nurses[nurseindex]
        for i in range(2, length):
            if current.chairs[chair][time + i] > 5:
                return False
        if current.chairs[chair][time + length - 2] > 1 or self.chairs[chair][time + length - 1] is 1:
            return False
        extra = -1
        if current.chairs[chair][time] > 0 or current.chairs[chair][time+1] > 0:
            for i in range(len(self.nurses)):
                for j in range(3):
                    if self.nurses[i].chairs[j][time] is not 1 and self.nurses[i].chairs[j][time] is not 2 and \
                                    self.nurses[i].chairs[j][time + 1] is not 1 and self.nurses[i].chairs[j][
                                time + 1] is not 2 and extra is -1:
                        extra = [i, j]
                        break
        for i in range(2, length):
            if current.chairs[chair][time + i] is 1:
                return 1
        # return False
        # if (self.chairs[chair][time] > 0 or self.chairs[chair][time+1] > 0):
        #     return False
        # for i in range(2, appointment):
        #     if self.chairs[chair][time + i] > 2:
        #         return False
        # if self.chairs[chair][time + appointment - 2] > 0 or self.chairs[chair][time + appointment - 1] > 0:
        #     return False
        # for i in range(2, appointment):
        #     if self.chairs[chair][time + i] is 1:
        #         other_index = self.check_other_nurses(nurses, self.lunch)
        # return True
        return -1


class Appointment:
    def __init__(self, length, nurse, chair, time):
        self.length = length
        self.nurse = nurse
        self.chair = chair
        self.time = time
