//-----------------Handles Schedule Inputs--------------//

    const SPANBOLD = "<span style='font-weight:bold'>";
    const ENDSPANBOLD = "</span>";

/*
   Function: removeOptions

   Clears the dropdown menu that occurs when loading saved schedules and time slots.

   Parameters:

      selectbox - identifier for dropdown menu

   Returns:

      None
 */
    function removeOptions(selectbox) {
        var i;
        for(i=selectbox.options.length-1;i>=0;i--)
            selectbox.remove(i);
    }

/*
   Function: SaveSchedule

   Gets called once user clicks save button from popup menu.
   Handles saving the RN schedules to the database through an AJAX call.
   Handles same name schedules and overriding previous saved schedules.
   Handles saving by going through each row in the table and stores the
   information into var Nurse.
   Notifies user if save was successful or not.

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN
      overwrite - Used to identify if user wants to overwrite prev schedule

   Returns:

      boolean - true if successful save; false if otherwise
 */
    function SaveSchedule(prefix, overwrite){
        var ScheduleGroup = $('#id_ScheduleGroupName').val();
        var alert = document.getElementById("save_alert");
        $('#yesOverwrite').hide();
        $('#noOverwrite').hide();
        $('#save_alert').hide();
        $('#id_ScheduleGroupName').attr('readonly','readonly');

        if(ScheduleGroup.match(/[\w+\.\_]+/)) {
            var alreadyExists = ScheduleNameUsed(ScheduleGroup);
            if(alreadyExists && overwrite == false)     //ask the user if they want to overwrite
            {
                $('#save_alert').show();
                alert.innerHTML = 'That name is already used. Would you like to overwrite it?';
                $('#yesOverwrite').show();
                $('#noOverwrite').show();
                return false;
            }
            else if(alreadyExists && overwrite == true)  //delete so we can overwrite
            {
                $.ajax({
                    type: 'GET',
                    dataType: 'html',
                    url: '/delete_schedule_group/',
                    contentType: "application/json",
                    data: {'ScheduleGroupName': ScheduleGroup}
                });
            }

            var table = document.getElementById(prefix + 'Table');
            for (var i = 1; i < table.rows.length - 1; i++) {
                var row = table.rows[i];
                var nurse = {
                    'ScheduleGroupName': ScheduleGroup,
                    'Team': row.cells[2].firstChild.value,
                    'StartTime': row.cells[3].firstChild.value,
                    'LunchTime': row.cells[4].firstChild.value,
                    'LunchDuration': row.cells[5].firstChild.value,
                    'EndTime': row.cells[6].firstChild.value
                };
                $.ajax({
                    type: 'GET',
                    dataType: 'html',
                    url: '/add_to_schedule_group/',
                    contentType: "application/json",
                    data: nurse
                });
            }
            var label = $("#pageAlert");
            label.text(ScheduleGroup + ' has been saved');
            label.css("display", "block");
            label.addClass("alert-success").removeClass("alert-danger");
            return true;
        }
        else {
            $('#id_ScheduleGroupName').attr('readonly','false');
            alert.show();
            alert.text(ScheduleGroup + ' is not a valid ScheduleName');
            return false;
        }
    }

/*
   Function: LoadSchedule

   Gets called once user hits load button from popup menu.
   Handles loading the RN schedules from database through AJAX call.
   If AJAX call is successful, calls fillRNSchedule

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      None
 */
    function LoadSchedule(prefix){
        var label = $("#pageAlert"); //hide any possible existing notifications
        label.css("display", "none");
        var ScheduleGroup = $("#savedSchedules option:selected").html();
        label.innerHTML = ''; //clear any previous alerts
        label.hide();
        if(ScheduleGroup.match(/[\w+\.\_]+/)) {
            $.ajax({
                type: 'GET',
                dataType: 'html',
                url: '/load_schedule_group/',
                contentType: "application/json",
                data: {'ScheduleGroupName': ScheduleGroup},
                complete: function(response, textStatus) {
                    if(textStatus != 'success')
                        return alert(textStatus + ': ' + response.responseText);
                },
                success: function(result) {
                    var objectList = JSON.parse(result);
                    fillRNSchedule(objectList, prefix);
                }
            });
        }
    }

/*
   Function: ScheduleNameUsed

   Checks if ScheduleGroup (name of Schedule) is stored in database.
   Used in SaveSchedule function, overwrite section.

   Parameters:

      ScheduleGroup - Name of schedule that user wants to save.

   Returns:

      returnValue - boolean, false if unique name, true if otherwise
 */
    function ScheduleNameUsed(ScheduleGroup){
        if(ScheduleGroup.match(/[\w+\.\_]+/)) {
            var returnValue = false;
            $.ajax({
                type: 'GET',
                dataType: 'html',
                url: '/check_schedule_group_name/', //url from url.py
                contentType: "application/json",
                data: {'ScheduleGroupName': ScheduleGroup}, //our var names
                async: false,
                complete: function(response, textStatus) {
                    if(textStatus != 'success')
                        return alert(textStatus + ': ' + response.responseText);
                },
                success: function(result) {
                    if(result == 'True')
                        returnValue = false; //unique
                    else
                        returnValue = true; //already used
                }
            });
            return returnValue;
        }
    }

/*
   Function: LoadScheduleNames

   Gets called once user hits Load Nurse Schedule button.
   Does AJAX call to load up all saved schedule's names.

   Parameters:

      None

   Returns:

      None
 */
    function LoadScheduleNames(){
        $.ajax({
            type: 'GET',
            url: '/load_schedule_group_names/',
            contentType: "application/json",
            complete: function(response, textStatus) {
                if(textStatus != 'success')
                    return alert(textStatus + ': ' + response.responseText);
            },
            success: function(result) {
                var count = result.length;
                var select = $('#savedSchedules');

                //clear current options
                removeOptions(document.getElementById("savedSchedules"));

                //add the loaded options
                for(var i = 0; i < count; i++)
                {
                    var name = result[i].pk;
                    select.append(new Option(name, name));
                }
            }
        });
    }

/*
   Function: fillRNSchedule

   Fills up RN table information of loaded schedule by going through each row and adding the information.
   Removes previous RN table information after loading.

   Parameters:

      objectList - Contains information of saved RN schedules (Team, StartTime, etc)
      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      None
 */
    function fillRNSchedule(objectList, prefix){
        objectList = objectList.sort(compareRNSchedules);
        var count = objectList.length;
        var table = document.getElementById(prefix + 'Table');
        var tableRows = table.rows.length - 2; //one row is header and one is add button

        if(tableRows < count) //need to add rows
            while(tableRows != count) {
                AddRowClick(prefix);
                tableRows++;
            }
        else if(tableRows > count) //need to remove extra rows
            while(tableRows != count) {
                RemoveRowClick(tableRows,prefix);
                tableRows--;
            }

        for(var i = 0; i < count; i++)
        {
            var row = table.rows[i+1];
            var obj = objectList[i].fields;
            row.cells[2].firstChild.value = obj.Team;
            row.cells[3].firstChild.value = obj.StartTime;
            row.cells[4].firstChild.value = obj.LunchTime;
            row.cells[5].firstChild.value = obj.LunchDuration;
            row.cells[6].firstChild.value = obj.EndTime;
        }
    }

/*
   Function: compareRNSchedules

   Used when sorting.
   Sorts by team and then StartTime.

   Parameters:

      s1 - first RN object for comparison
      s2 - second RN object for comparison

   Returns:

      -1 - if s1 < s2
      0 - if s1 is equal to s2
      1 - if s1 > s2
 */
    function compareRNSchedules(s1, s2){
        if(s1.fields.Team == s2.fields.Team)
        {
            if(s1.fields.StartTime == s2.fields.StartTime)
                return 0;
            else if(s1.fields.StartTime > s2.fields.StartTime)
                return 1;
            else return -1;
        }
        else if(s1.fields.Team > s2.fields.Team)
            return 1;
        else return -1;
    }
/*
   Function: updateElementIndex

   Maintains tables with dynamic number of rows.
   Handles the logic to maintain ID is correct per row.
   Used when adding or deleting rows.
   Ex: 4 nurses 1-4. Delete first row. nurses 2-4. Changes identifier to nurses 1-3.

   Parameters:

      object - used to identify the button for deletion/insertion of rows
      prefix - Used for identifying elements on table by ID. ex: RN
      index - used for identifying which row is currently being updated

   Returns:

      None
 */
    function updateElementIndex(object, prefix, index) {
		var id_regex = new RegExp('(' + prefix + '-\\d+)');
		var replacement = prefix + '-' + index;
		if ($(object).attr("for")) $(object).attr("for", $(object).attr("for").replace(id_regex, replacement));
		if (object.id) object.id = object.id.replace(id_regex, replacement);
		if (object.name) object.name = object.name.replace(id_regex, replacement);
        if (object.className && object.className == "delete-button")
            $(object).removeAttr("onclick").unbind().click(function () {
                    RemoveRowClick(index+1, prefix);
            });
	}

/*
   Function: buttonDayClick

   Does nothing.

   Parameters:

      None

   Returns:

      None
 */
    function buttonDayClick() {}
/*
   Function: AddRowClick

   Gets called once user hits (+) button to add an additional row to a table.
   Adds a row while maintaining IDs are maintained correctly.

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      None
 */
    function AddRowClick(prefix) {
        try {
            var form_count = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
            if(form_count == 1 ) //if there was only one row, enable the delete button again
            {
                var table = document.getElementById(prefix + 'Table');
                var lastDeleteButton = table.rows[1].cells[0].children[0];
                lastDeleteButton.disabled = false;
            }
            var row = $('.dynamic-' + prefix + '-row:first').clone(true).get(0);
            row.id = prefix + '-row-' + (form_count+1); //table row number starting at 1
            $(row).insertAfter($('.dynamic-' + prefix + '-row:last'));
            $(row).children().children().each(function () {
                updateElementIndex(this, prefix, form_count);
                $(this).val('');
            });
            if(prefix == "RN")
                row.cells[1].textContent =  'Nurse ' + (form_count + 1);
            $('#id_' + prefix + '-TOTAL_FORMS').val(form_count + 1);
        }catch(e) {
            alert(e);
        }
    }
/*
   Function: RemoveRowClick

   Gets called once user hits (-) button to delete specific row from table.
   Deletes a row while maintaining IDs are maintained correctly.

   Parameters:

      rowIndex - Used to identify which row is to be deleted
      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      None
 */
    function RemoveRowClick(rowIndex, prefix){
         var form_count = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
         try {
            var table = document.getElementById(prefix + 'Table');
            table.deleteRow(rowIndex);

            for(var tableIndex=1; tableIndex < form_count; tableIndex++) {
                var row = table.rows[tableIndex];
                var RNNumber = tableIndex - 1;
                if(row.id.split('-')[2] != tableIndex) { //If the ID does not match the row number
                    row.id = prefix + '-row-' + tableIndex;
                    $(row).children().children().each(function () {
                        updateElementIndex(this, prefix, RNNumber);
                    });
                    if(prefix == "RN")
                        row.cells[1].textContent =  'Nurse ' + tableIndex;
                }//end if
            }//end for loop
             $('#id_' + prefix + '-TOTAL_FORMS').val(--form_count);
         }
         catch(e) {
                alert(e);
            }
        if(form_count == 1 ) //if there is now only one row left, disable delete button
        {
            var lastDeleteButton = table.rows[1].cells[0].children[0];
            lastDeleteButton.disabled = true;
        }
    }
/*
   Function: GetTotalAppointmentMinutes

   Grabs the total appointment minutes.

   Parameters:

      AppPrefix - Used for identifying the table

   Returns:

      totalminutes - Total minutes from appointment
 */
    function GetTotalAppointmentMinutes(AppPrefix){
        var table = document.getElementById(AppPrefix + 'Table');
        if(table == null) return 0;
        var totalminutes = 0;
        for(var i=1; i < table.rows.length-1; i++){
            var dropdown = table.rows[i].cells[1].children[0];
            var count = table.rows[i].cells[2].children[0];
            if (dropdown.selectedIndex < 0 || count.valueAsNumber < 1)
                continue;
            var mins = parseInt(dropdown.options[dropdown.selectedIndex].value);
            totalminutes += mins  * count.valueAsNumber;
        }
        return totalminutes;
    }
/*
   Function: GetTotalRNMinutes

   Grabs the total RN minutes.

   Parameters:

      RNPrefix - Used for identifying the table
      chairs - Number of chairs per nurse

   Returns:

      totalminutes * chairs - All minutes for entire appointment
 */
    function GetTotalRNMinutes(RNPrefix, chairs){
        var table = document.getElementById(RNPrefix + 'Table');
        if(table == null) return 0;
        var totalminutes = 0;
        for(var i=1; i < table.rows.length-2; i++){
            var StartTime = table.rows[i].cells[3].children[0].value;
            var LunchDuration = table.rows[i].cells[5].children[0].value;
            var EndTime = table.rows[i].cells[6].children[0].value;
            try {
                var StartMinutes = parseInt(StartTime.split(':')[0] * 60) + parseInt(StartTime.split(':')[1]);
                var EndMinutes = parseInt(EndTime.split(':')[0] * 60) + parseInt(EndTime.split(':')[1]);
            }
            catch(err) {continue;}
            totalminutes += EndMinutes - StartMinutes - parseInt(LunchDuration);
        }
        return totalminutes * chairs;
    }

    //-----------------Actions for time-slot input----------------------
/*
   Function: ValidTimeSlotInput

   Validation for time slots.
   Alerts users if input is incorrect.

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      boolean - true if all inputs are valid, false if otherwise
 */
    function ValidTimeSlotInput(prefix){
        var alert = document.getElementById("appointment_alert");
        alert.innerHTML = ''; //clear any previous alerts
        $(alert).hide();
        var table = document.getElementById(prefix + 'Table');
        if(table.rows.length < 3){
            $(alert).show();
            alert.innerHTML = SPANBOLD + "Oops!" + ENDSPANBOLD + " Looks like you forgot to enter time slots";
            return false;
        }
        //loop through each row to ensure all fields are filled in
        for (var i = 1; i < table.rows.length - 1; i++) {
            var row = table.rows[i];
            var timePeriod = row.cells[1].firstChild.value;
            var num = row.cells[2].firstChild.value;
            if (timePeriod == "" || num == "") {
                $(alert).show();
                alert.innerHTML = SPANBOLD + "Oops!" + ENDSPANBOLD + " Looks like you forgot to fill in all the fields";
                return false;
            }
            if(isNaN(num) || num < 0){
                $(alert).show();
                alert.innerHTML = num + " is not a valid input";
                return false;
            }
        }
        return true;
    }
/*
   Function: SaveTimeSlotButtonClick

   Button for saving the time slots.

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

     None
 */
    function SaveTimeSlotButtonClick(prefix){
        $('#TimeSlotSaveName').removeAttr('readonly');
        if(ValidTimeSlotInput(prefix)) { //checks all fields in the table
            $('#yesOverwrite_app').hide();
            $('#noOverwrite_app').hide();
            $('#save_app_alert').hide();
            $('#saveTimeSlotModal').modal('show');
        }
    }
/*
   Function: TimeSlotNameUsed

   Checks if TimeSlot name is unique.
   Does AJAX call to check and compare with other previous saved timeslots.

   Parameters:

      TimeSlotGroup - name of Timeslot that user wants to save.

   Returns:

      returnValue - boolean value; false if unique name, true if otherwise
 */
    function TimeSlotNameUsed(TimeSlotGroup){
        if(TimeSlotGroup.match(/[\w+\.\_]+/)) {
            var returnValue = false;
            $.ajax({
                type: 'GET',
                dataType: 'html',
                url: '/check_time_slot_group_name/', //url from url.py
                contentType: "application/json",
                data: {'SaveName': TimeSlotGroup}, //our var names
                async: false,
                complete: function(response, textStatus) {
                    if(textStatus != 'success')
                        return alert(textStatus + ': ' + response.responseText);
                },
                success: function(result) {
                    if(result == 'False')
                        returnValue = false; //unique
                    else
                        returnValue = true; //already used
                }
            });
            return returnValue;
        }
    }
/*
   Function: SaveTimeSlots

   Gets called once user clicks save button from popup menu.
   Handles saving the TimeSlots to the database through an AJAX call.
   Handles same name TimeSlots and overriding previous saved TimeSLots.
   Notifies user if save was successful or not.

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN
      overwrite - Used to identify if user wants to overwrite prev TimeSlot

   Returns:

      boolean - true if successful save; false if otherwise
 */
    function SaveTimeSlots(prefix, overwrite){
        var SaveName = document.getElementById("TimeSlotSaveName").value; //grab save name from input box
        var alert = document.getElementById("save_app_alert");
        $('#yesOverwrite_app').hide();
        $('#noOverwrite_app').hide();
        $('#save_app_alert').hide();
        $('#TimeSlotSaveName').attr('readonly','readonly');

        if(SaveName.match(/[\w+\.\_]+/)) { //defining regex (stuff we accept)
            var alreadyExists = TimeSlotNameUsed(SaveName);
            var ajaxFailed = false;
            if(alreadyExists && overwrite == false)     //ask the user if they want to overwrite
            {
                $('#yesOverwrite_app').show();
                $('#noOverwrite_app').show();
                $('#save_app_alert').show();
                alert.innerHTML = 'That name is already used. Would you like to overwrite it?';
                return false;
            }
            else if(alreadyExists && overwrite == true)  //delete so we can overwrite
            {
                $.ajax({
                    type: 'GET',
                    dataType: 'html',
                    url: '/delete_time_slot/',  //changed and is now defined in urls.py
                    contentType: "application/json",
                    async: false,
                    data: {'SaveName': SaveName}, //overwrite name
                    complete: function(response, textStatus) {
                        if(textStatus != 'success') {
                            //alert(textStatus + ': ' + response.responseText);
                            ajaxFailed = true;
                        }
                    }
                });
            }
            //if we overwrite or we are successful, loop through and save values
            var table = document.getElementById(prefix + 'Table');
            for (var i = 1; i < table.rows.length - 1; i++) { //loop through each row and grab value in the input box
                if(ajaxFailed) break;
                var row = table.rows[i];
                if(row.cells[1].firstChild.value == null || row.cells[2].firstChild.value == null)
                    continue;
                var doNotWait = true;
                if(i == table.rows.length - 2) //last itteration
                    doNotWait = false;
                $.ajax({
                    type: 'GET',
                    dataType: 'html',
                    url: '/save_time_slot/',
                    async: doNotWait,
                    contentType: "application/json",
                    data: {'SaveName': SaveName, 'Duration': row.cells[1].firstChild.value, 'Count': row.cells[2].firstChild.value, 'Priority': i},
                    complete: function(response, textStatus) {
                        if(textStatus != 'success')
                            ajaxFailed = true;
                    }
                });
            }

            var label = $("#appointment_alert");
            if(ajaxFailed){
                label.text(SaveName + ' could not be saved');
                label.css("display", "block");
                label.addClass("alert-danger").removeClass("alert-success");
                return false;
            }
            label.text(SaveName + ' has been saved');
            label.css("display", "block");
            label.addClass("alert-success").removeClass("alert-danger");
            return true;
        }
        else {
            $('#TimeSlotSaveName').attr('readonly','false'); //if we dont accept it throw an error
            alert.show();
            alert.text(SaveName + ' is not a valid ScheduleName');
            return false;
        }
    }
/*
   Function: LoadTimeSlots

   Gets called once user hits load button from popup menu.
   Handles loading the TimeSlots from database through AJAX call.
   If AJAX call is successful, calls fillTimeSlots

   Parameters:

      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      None
 */
    function LoadTimeSlots(prefix){
        var alert = document.getElementById("appointment_alert");
        alert.innerHTML = ''; //clear any previous alerts
        $(alert).hide();
        $(alert).css("display", "none");//hide any possible existing notifications
        var TimeSlotGroup = $("#savedTimeSlots option:selected").html();
        $.ajax({
            type: 'GET',
            dataType: 'html',
            url: '/load_time_slot_group/',
            contentType: "application/json",
            data: {'SaveName': TimeSlotGroup},
            complete: function(response, textStatus) {
                if(textStatus != 'success')
                    alert(textStatus + ': ' + response.responseText);
            },
            success: function(result) {
                var objectList = JSON.parse(result);
                fillTimeSlots(objectList, prefix);
            }
        });
    }
/*
   Function: fillTimeSlots

   Fills up TimeSlots table information of loaded TimeSlots by going through each row and adding the information.
   Removes previous TimeSlots table information after loading.

   Parameters:

      objectList - Contains information of saved TimeSlots schedules (Duration and Count)
      prefix - Used for identifying elements on table by ID. ex: RN

   Returns:

      None
 */
    function fillTimeSlots(objectList, prefix){
        if(objectList.length == 0) {
            document.getElementById("appointment_alert").innerHTML =
                SPANBOLD + "Uh oh," + ENDSPANBOLD + " we were unable to load the requested time slot input";
            return;
        }
        var count = objectList.length;
        var table = document.getElementById(prefix + 'Table');
        var tableRows = table.rows.length - 2; //one row is header and one is add button

        if(tableRows < count) //need to add rows
            while(tableRows != count) {
                AddRowClick(prefix);                    // may have to make my own version of this
                tableRows++;
            }
        else if(tableRows > count) //need to remove extra rows
            while(tableRows != count) {
                RemoveRowClick(tableRows,prefix);       //// may have to make my own version of this
                tableRows--;
            }

        for(var i = 0; i < count; i++)
        {
            var row = table.rows[i+1];
            var obj = objectList[i].fields;
            row.cells[1].firstChild.value = obj.Duration;
            row.cells[2].firstChild.value = obj.Count;
        }
    }

/*
   Function: LoadTimeSlotNames

   Gets called once user hits Load TimeSlot button.
   Does AJAX call to load up all TimeSlot's names.

   Parameters:

      None

   Returns:

      None
 */
    function LoadTimeSlotNames(){
        $.ajax({
            type: 'GET',
            url: '/load_time_slot_group_names/',
            contentType: "application/json",
            complete: function(response, textStatus) {
                if(textStatus != 'success')
                    return alert(textStatus + ': ' + response.responseText);
            },
            success: function(result) {
                var count = result.length;
                var select = $('#savedTimeSlots');
                //clear current options
                removeOptions(document.getElementById("savedTimeSlots"));
                //add the loaded options
                for(var i = 0; i < count; i++)
                    select.append(new Option(result[i].pk, result[i].pk));
            }
        });
    }
/*
   Function: PrepopulateTimeslots

   Prepopulates timeslots with values from AppointmentForm.TIMESLOTS
   Populates each timeslow row with each TIMESLOTS

   Parameters:

      prefix - used to identify row ex: RN
      tslots - list of TIMESLOTS

   Returns:

      None
 */
    function PrepopulateTimeslots(prefix, tslots) {
        var table = document.getElementById(prefix + 'Table');
        var tableRows = table.rows.length - 2;
        if(tableRows < tslots.length)
            while(tableRows != tslots.length) {
                AddRowClick(prefix);
                tableRows++;
            }
        else if(tableRows > tslots.length)
            while(tableRows != tslots.length) {
                RemoveRowClick(tableRows,prefix);
                tableRows--;
            }
        for (var i = 0; i < tslots.length; i++) {
            var row = table.rows[i+1];
            row.cells[1].firstChild.value = tslots[i];
            row.cells[2].firstChild.value = 0;
            row.cells[3].firstChild.selectedIndex = 0;
        }
    }

