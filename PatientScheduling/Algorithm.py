

def insert_slot(length, array, chair, numNurse):
	nurseCol =numNurse*3 #looks cleaner this way
	for i in array:
		if i == 2:
			continue
		elif 2 in array[i:i+length,numNurse*3+chair]:
			continue
		else: #schedule slot and mark the other chairs
			array[i:i+length, nurseCol+chair] =2
			if chair == 0:
				array[i:i+2, nurseCol+1] =2 #beginings
				array[i:i+2, nurseCol+2] =2
				array[i+length-2:i+length, nurseCol+1] =2 #ends
				array[i+length-2:i+length, nurseCol+2] =2
			if chair == 1:
				array[i:i+2, nurseCol+chair-1] =2 #beginings
				array[i:i+2, nurseCol+chair+1] =2
				array[i+length-2:i+length, nurseCol] =2 #ends
				array[i+length-2:i+length, nurseCol+2] =2
			if chair ==2:
				array[i:i+2, nurseCol] =2 #beginings
				array[i:i+2, nurseCol+1] =2
				array[i+length-2:i+length, nurseCol] =2 #ends
				array[i+length-2:i+length, nurseCol+1] =2
			return True
	return False

def schedule_slots(slots, nurses):
    #nurse input is (nurse id, lunch time, start time, end time)
    #slots input is (length, #)
    #this is assuming our input is in military time
    schedule = [[0 for x in range(3*len(nurses))] for x in range(37)]
    #schedule nurse lunches and absence periods
    i = 0
    for (nurse_id, lunch, start, end) in nurses:
    #if lunch is at 13:00 want the 19-23th slot
        schedule[lunch:lunch+4,i*3:i*3+3] = 1  #1 denotes a lunch break, which can be scheduled for
        if start !=0:
            schedule[0:start,i*3:i*3+3] = 2  #2 denotes either a scheduled slot or that they are not at the hospital
        if end != 37:
            schedule[end+1:37,i*3:i*3+3] = 2
        i += 1
	print schedule
	#now to schedule the slots
	#while slots != Null	#while we still have slots left

#	for(length, quantity) in slots: #for every slot
#		Empty = False
#		for chair in xrange(3):	#for every chair
#			for nurse in xrange(len(nurses)): #for every nurse
#				if quantity ==0:
#					break
#				inserted = insert_slot(length,schedule, chair, nurse)
#				if inserted == True:
#					quantity-=1



nurse_input = [(1, 19, 0, 31), (1, 15, 0, 31), (1, 19, 0, 31), (1, 19, 3, 37), (1, 23, 3, 37), (1, 11, 3, 37)]
slots_input = [(420, 3), (360, 3), (330, 2), (300, 3), (270, 3)]
for (length, quantitiy) in slots_input:
    length = length/15
schedule_slots(slots_input,nurse_input)
