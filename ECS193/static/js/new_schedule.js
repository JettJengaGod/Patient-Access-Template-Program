

    function removeOptions(selectbox) {
        var i;
        for(i=selectbox.options.length-1;i>=0;i--)
            selectbox.remove(i);
    }

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
            document.getElementById("pageAlert").innerHTML = ScheduleGroup + ' has been saved';
            return true;
        }
        else {
            $('#id_ScheduleGroupName').attr('readonly','false');
            alert.show();
            alert.innerHTML = ScheduleGroup + ' is not a valid ScheduleName';
            return false;
        }
    }
    function LoadSchedule(prefix){
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
                    fillRNSchedule(objectList, prefix)
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
                url: '/check_schedule_group_name/',
                contentType: "application/json",
                data: {'ScheduleGroupName': ScheduleGroup},
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
