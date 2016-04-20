

    //removes all listed options in dropdown list
    function removeOptions(selectbox) {
        var i;
        for(i=selectbox.options.length-1;i>=0;i--)
            selectbox.remove(i);
    }

    //Actions for nurse schedule groups
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
    function LoadSchedule(prefix){
        var label = $("#pageAlert"); //hide any possible existing notifications
        label.css("display", "none");
        var ScheduleGroup = $("#savedSchedules option:selected").html();
        document.getElementById("pageAlert").innerHTML = ''; //clear any previous alerts
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
    //used when sorting. returns negative if s1 < s2, 0 if s1=s2, and positive if s1 > s2
    //compares team, then StartTime
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
    //maintains tables with dynamic # of rows
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
    function buttonDayClick() {}
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
    function GetTotalRNMinutes(RNPrefix){
        var table = document.getElementById(RNPrefix + 'Table');
        if(table == null) return 0;
        var chairs = document.getElementById('id_NumberOfChairs').valueAsNumber;
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
    //------------------------------------------------------------------------------------------------------------

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
                    if(result == 'True')
                        returnValue = false; //unique
                    else
                        returnValue = true; //already used
                }
            });
            return returnValue;
        }
    }
    //for saving the time slots
    function SaveTimeSlots(prefix, overwrite){
        var TimeSlotGroup = $('#id_TimeSlotGroupName').val(); //grab save name from input box
        var alert = document.getElementById("save_time_slot_alert");
        $('#yesOverwrite').hide();
        $('#noOverwrite').hide();
        $('#save_alert').hide();
        $('#id_TimeSlotGroupName').attr('readonly','readonly');

        if(TimeSlotGroup.match(/[\w+\.\_]+/)) { //defining regex (stuff we accept)
            var alreadyExists = TimeSlotNameUsed(TimeSlotGroup);
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
                    url: '/delete_time_slot/',  //changed and is now defined in urls.py
                    contentType: "application/json",
                    data: {'SaveName': TimeSlotGroup} //overwrite name
                });
            }
            //if we overwrite or we are successful, loop through and save values
            var table = document.getElementById(prefix + 'Table');
            for (var i = 1; i < table.rows.length - 1; i++) { //loop through each row and grab value in the input box
                var row = table.rows[i];
                $.ajax({
                    type: 'GET',
                    dataType: 'html',
                    url: '/save_time_slot/', //saved schedule*****************************
                    contentType: "application/json",
                    data: {'SaveName': TimeSlotGroup, 'Duration': row.cells[1].firstChild.value, 'Count': row.cells[2].firstChild.value}
                });
            }
            var label = $("#pageAlert");
            label.text(TimeSlotGroup + ' has been saved');
            label.css("display", "block");
            label.addClass("alert-success").removeClass("alert-danger");
            return true;
        }
        else {
            $('#id_TimeSlotGroupName').attr('readonly','false'); //if we dont accept it throw an error
            alert.show();
            alert.text(TimeSlotGroup + ' is not a valid ScheduleName');
            return false;
        }
    }
    function LoadTimeSlots(prefix){
        var label = $("#pageAlert"); //hide any possible existing notifications
        label.css("display", "none");
        var TimeSlotGroup = $("#savedTimeSlots option:selected").html();
        document.getElementById("pageAlert").innerHTML = ''; //clear any previous alerts
        if(TimeSlotGroup.match(/[\w+\.\_]+/)) {
            $.ajax({
                type: 'GET',
                dataType: 'html',
                url: '/load_time_slot_group/',
                contentType: "application/json",
                data: {'SaveName': TimeSlotGroup},
                complete: function(response, textStatus) {
                    if(textStatus != 'success')
                        return alert(textStatus + ': ' + response.responseText);
                },
                success: function(result) {
                    var objectList = JSON.parse(result);
                    fillTimeSlots(objectList, prefix);   // need to update this funtion*************************
                }
            });
        }
    }
    function fillTimeSlots(objectList, prefix){       //currently working on this*************
        objectList = objectList.sort(compareTimeSlots);
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
    //used when sorting. returns negative if s1 < s2, 0 if s1=s2, and positive if s1 > s2
    //compares team, then StartTime
    function compareTimeSlots(s1, s2){
        if(s1.fields.Duration == s2.fields.Duration)
        {
                return 0;

        }
        else if(s1.fields.Duration > s2.fields.Duration)
            return 1;
        else return -1;
    }

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
                var select = $('#savedTimeSlots');              // what do I put here *********************************

                //clear current options
                removeOptions(document.getElementById("savedTimeSlots"));

                //add the loaded options
                for(var i = 0; i < count; i++)
                {
                    var name = result[i].pk;
                    select.append(new Option(name, name));
                }
            }
        });
    }

