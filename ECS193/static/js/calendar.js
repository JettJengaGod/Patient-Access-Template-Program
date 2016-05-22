

//-----------------Handling Chemotherapy Drug--------------//

/*
   Function: DrugSelected

   Uses Ajax to get the chemotherapy drug rules and other information from the database, get the text rules,
   then calls highlight() to apply them to the calendar view

   Parameters:

      None

   Returns:

      None

    See Also:

      <highlight>


*/
function DrugSelected(){
    var dropdown = document.getElementById('drugDropdown');
    var rulesLabel = document.getElementById('drugRules');
    var name = dropdown.options[dropdown.selectedIndex].value;
    if(name != "NULL") {
        $.ajax({
            type: 'GET',
            dataType: 'html',
            url: '/load_chemotherapy_drug/',
            contentType: "application/json",
            data: {'Name': name},
            complete: function (response, textStatus) {
                if (textStatus != 'success')
                    alert(textStatus + ': ' + response.responseText);
            },
            success: function (result) {
                var drug = JSON.parse(result)[0].fields;
                rulesLabel.innerText = drug.OtherRules;
                highlight(drug.EarliestTime, drug.LatestTime)
            }
        });
    }
    else {
        highlight();
        rulesLabel.innerText = "";
    }
}
/*
   Function: highlight

   After parsing the time value information from the parameters it then uses it to fade the time slots that do not
   fall into the specified time frame for the selected drug.

   Parameters:

      earliest - earliest time the drug can be scheduled
      latest - latest time the drug can be scheduled

   Returns:

      None



*/
function highlight(earliest, latest){
    var allApps = $('.appt');
    if(earliest == null && latest == null){
        allApps.each(function(){
            this.style.opacity = '1';
        });
        return;
    }
    var earliestStartHour=-1, earliestStartMin=0, latestEndHour=100, latestEndMin=0;
    if(earliest != null) {
        earliestStartHour = parseInt(earliest.split(':')[0]);
        earliestStartMin = parseInt(earliest.split(':')[1]);
    }
    if(latest != null) {
        latestEndHour = parseInt(latest.split(':')[0]);
        latestEndMin = parseInt(latest.split(':')[1]);
    }
    allApps.each(function(){
        var x = $(this);
        var tempStartHour = parseInt(x.attr('startTime').split(':')[0]);
        var tempStartMin = parseInt(x.attr('startTime').split(':')[1]);
        var tempEndHour = parseInt(x.attr('endTime').split(':')[0]);
        var tempEndMin = parseInt(x.attr('endTime').split(':')[1]);
        if(tempStartHour < earliestStartHour || tempEndHour > latestEndHour
            || (tempStartHour == earliestStartHour && tempStartMin < earliestStartMin)
            || (tempEndHour == latestEndHour && tempEndMin > latestEndMin)
        ) {
            this.style.opacity = '.25';
        }
        else {
            this.style.opacity = '1';
        }
    });
}

//-----------------Displaying the Calendar--------------//
/*
   Function: BuildRNRow

   Builds a nurse row (without the appointments) on the calendar.

   Parameters:

      RNIndex - the ID of the Nurse (they are passed in sequentially i.e. 1, 2, 3...)
      startTime - the time when the nurse starts for the day
      lunchTime -the time when the nurse's lunch starts for the day
      duration - how long the lunch is
      endTime - the time when the nurse ends for the day
      closeTime - the time when the chemotherapy facility ends for the day

   Returns:

      None

   See Also:

      <AddFill>

*/
function BuildRNRow(RNIndex, startTime, lunchTime, duration, endTime, closeTime) {
    var table = document.getElementById("calendar");
    var maxCellIndex = table.rows[0].cells.length - 2;
    var offset = closeTime - maxCellIndex; //used to calculate row index from given hour
    var i = 0;

    var row = document.getElementById("RN-"+RNIndex+"-row-"+i);
    while(row)
    {
        //block out times before nurse arrives
        var startTimeCell = row.cells[startTime.split(':')[0]-offset];
        var startTimePercent = (startTime.split(':')[1])/60;
        var j = 0;
        while(j < startTime.split(':')[0]-offset)
            AddFill(row.cells[j++],1,'unavailable',true);
        if(startTimePercent > 0)
            AddFill(startTimeCell,startTimePercent,'unavailable',true);

        //Mark lunch
        var LunchIndex = lunchTime.split(':')[0]-offset;
        var lunchTimeMinutes = parseInt(lunchTime.split(':')[1]);
        var remaining = duration;
        //handle case that lunch doesn't start on the hour
        if(lunchTimeMinutes > 0) {
            if(60 - lunchTimeMinutes > duration) //if it shouldn't fill the rest of the block
            {
                AddFill(row.cells[LunchIndex], 1 - (lunchTimeMinutes + duration) / 60, 'filler', false);
                AddFill(row.cells[LunchIndex++], 1 - duration/60, 'lunch', false);
                remaining = 0;
            }
            else {
                AddFill(row.cells[LunchIndex++], 1 - lunchTimeMinutes / 60, 'lunch', false);
                remaining -= 60 - lunchTimeMinutes;
            }
        }
        //handle lunches that are more than one hour
        while(remaining >= 60) { //if the total remaining lunch duration is greater than 60 minutes
            AddFill(row.cells[LunchIndex++],1,'lunch',true);
            remaining -= 60;
        }
        //handle lunches greater than one hour but don't end on the hour
        if(remaining > 0)
            AddFill(row.cells[LunchIndex],remaining/60,'lunch',true);

        //Mark times after RN leaves as unavailable
        var endTimeIndex = endTime.split(':')[0]-offset;
        var endTimePercent = (endTime.split(':')[1])/60;
        if(endTimePercent == 0 && endTimeIndex <= maxCellIndex)
            AddFill(row.cells[endTimeIndex++],1,'unavailable',true);
        else if(endTimePercent > 0)
            AddFill(row.cells[endTimeIndex++],1 - endTimePercent,'unavailable',false);
        while (endTimeIndex <= maxCellIndex) {
            AddFill(row.cells[endTimeIndex], 1, 'unavailable', true);
            endTimeIndex++;
        }

        i++;
        row = document.getElementById("RN-"+RNIndex+"-row-"+i);
    }
}
/*
   Function: AddAppointment

   puts an appointment on the calendar.

   Parameters:

      RNIndex - the ID of the Nurse the appointment is being scheduled over
      chairIndex - which chair the appointment will be scheduled under
      startTime - the time when the appointment starts
      endTime - the time when the appointment ends
      appID - ID of the appointment
      closeTime - the time when the chemotherapy facility ends for the day

   Returns:

      None

   See Also:

      <BuildApptDiv>
      <AddFill>

*/
var lastEndIndex = 0;
var lastEndPercent = 0;
var lastRNIndex = 1;
function AddAppointment(RNIndex, chairIndex, startTime, endTime, apptID, closeTime) {
    var row = document.getElementById("RN-"+RNIndex+"-row-"+chairIndex);
    var maxCellIndex = row.cells.length - 1;
    var offset = closeTime - maxCellIndex; //used to calculate row index from given hour
    if(lastRNIndex != RNIndex){
        lastEndIndex = 0;
        lastEndPercent = 0;
        lastRNIndex = RNIndex;
    }

    var startIndex = startTime.split(':')[0] - offset;
    var startMinutes = parseInt(startTime.split(':')[1]);
    var startPercent = startMinutes/60;
    var endIndex = endTime.split(':')[0] - offset;
    var endMinutes = parseInt(endTime.split(':')[1]);
    var endPercent = endMinutes/60;
    var totalTime = (endIndex*60 + endMinutes) - (startIndex*60 + startMinutes);
    var DurationCell = row.cells[MiddleCell(startIndex, endIndex)]; //The cell to put the duration name in
    var startdiv, enddiv;
    var startPlaced = false;
    // appointment doesn't start on the hour
    if (startMinutes > 0) {
        //right shift
        if (startIndex != endIndex) {
            var cell = row.cells[startIndex++];
            startdiv = BuildApptDiv(cell, 1 - startPercent, false, cell == DurationCell, apptID, startTime, endTime);
            startPlaced = true;
            totalTime -= (60 - startMinutes);
        }
        // special case middle appointment
        else {
            // there is an appointment that goes into table cell; recalculate filler
            if (startIndex == lastEndIndex) {
                AddFill(row.cells[startIndex], (startPercent - lastEndPercent), 'filler', true);
            }
            else {
                AddFill(row.cells[startIndex], startPercent, 'filler', true);
            }
            var cell = row.cells[startIndex];
            startdiv = BuildApptDiv(cell, (endPercent - startPercent), true, cell == DurationCell, apptID, startTime, endTime);
            startPlaced = true;
            totalTime = 0;
            endMinutes = 0;
        }
    }
    // appointment doesn't end on the hour
    var endPlaced = false;
    if (endMinutes > 0) {
        var cell = row.cells[endIndex];
        enddiv = BuildApptDiv(cell, endPercent, true, cell == DurationCell, apptID, startTime, endTime);
        totalTime -= endMinutes;
        if(!startPlaced) {
            startdiv = enddiv;
            startPlaced = true;
        }
        endPlaced = true;
        enddiv.style.borderRight = 'black solid 1px';
    }
    // fills out entire hour slot
    while (totalTime > 0) {
        var cell = row.cells[startIndex++];
        enddiv = BuildApptDiv(cell, 1, true, cell == DurationCell, apptID, startTime, endTime);
        if(!startPlaced) {
            startdiv = enddiv;
            startPlaced = true;
        }
        totalTime -= 60;
    }
    lastEndIndex = endIndex;
    lastEndPercent = endPercent;

    //add borders to divs
    if(startTime.split(':')[0] - offset == endIndex || (endMinutes == 0 && startTime.split(':')[0] - offset == endIndex - 1)){
        startdiv.style.borderLeft = 'black solid 1px';
        startdiv.style.borderRight = 'black solid 1px';
    }
    else {
        startdiv.style.borderLeft = 'black solid 1px';
        if (!endPlaced) enddiv.style.borderRight = 'black solid 1px';
    }
}
/*
   Function: Reserve

   reserves an appointment on the calendar.

   Parameters:

      appID - ID of the appointment to be reserved

   Returns:

      None

*/
function Reserve(apptID){
    $('.appt-'+apptID).each(function () {
        var x = $(this);
        x.addClass("appt-reserved");
        var str = "<br><span style='color: orange'>USER RESERVED</span>";
        x.attr('data-content', x.attr('data-content')+str);
    });
}
/*
   Function: AddFill

   Dynamically fills the appointment based on the parameters.

   Parameters:

      cell - cell to be filled
      fraction - fraction of the cell to be filled by this call
      classname - to be applied to the cell
      leftAligned - boolean on whether the cell is left aligned

   Returns:

      div -  the constructed div to apply to the portion of the cell

   See Also:

      <BuildApptDiv>

*/
function AddFill(cell, fraction, className, leftAligned){
    if(fraction > 1 || fraction < 0)
    {
        alert("The given fraction to fill the cell by is not a valid percent!")
        return;
    }

    cell.style.padding = 0;
    var div = document.createElement('div');

    if (!leftAligned) {
        if (className == "lunch")//lunch divs can not be floated or they will refuse to overlap
            div.style.marginLeft = (1 - fraction) * 100 + '%';
        else
            div.style.float = 'right';
    }
    div.innerHTML = '&nbsp;';
    div.className += ' ' + className;
    div.style.width = (fraction * 100) + '%';
    cell.appendChild(div);
    return div;
}
/*
   Function: BuildApptDiv

   Dynamically builds the html div for the appointment (similar to function AddFill except with appointment only attributes)
   BuildApptDiv(cell, endPercent, true, cell == DurationCell, apptID, startTime, endTime);
   Parameters:

      cell - cell to be filled
      fraction - fraction of the cell to be filled by this call
      leftAligned - boolean on whether the cell is left aligned
      showDuration - boolean on whether the to isplay the duration in this cell
      id - Id of the appointment this cell is a part of
      startTime - the time when the appointment that encompasses this cell starts (or at least the part of this cell that we are filling)
      endTime - the time when the appointment that encompasses this cell ends (or at least the part of this cell that we are filling)
      vorder - where to put the border to separate this appointment from the next

   Returns:

      div -  the constructed div to apply to the portion of the cell

   See Also:

      <BuildApptDiv>

*/
function BuildApptDiv(cell, fraction, leftAligned, showDuration, id, startTime, endTime, border) {
    if(fraction > 1 || fraction < 0)
    {
        alert("The given fraction to fill the cell by is not a valid percent!");
        return;
    }

    cell.style.padding = 0;
    var div = document.createElement('a');

    var EndHour = endTime.split(':')[0];
    var EndMinutes = endTime.split(':')[1];
    var StartHour = startTime.split(':')[0];
    var StartMinutes = startTime.split(':')[1];
    var minutes = (EndHour - StartHour)*60  + (EndMinutes - StartMinutes);
    var colorClass = "appt"+minutes;
    var durationText = getStringDuration(minutes);

    if(border != null && border != "")
    {
        if(border == "left")
            div.style.borderLeft = 'black solid 1px';
        else if(border == "right")
            div.style.borderRight = 'black solid 1px';
    }
    if (!leftAligned)
        div.style.float = 'right';
    var innertext = '&nbsp;';
    div.className += ' appt-' + id;
    div.setAttribute('apptSet', id);
    div.setAttribute('role', 'button');
    div.setAttribute('data-toggle', 'popover');
    div.setAttribute('data-trigger', 'focus');
    div.setAttribute('data-placement', 'top');
    div.setAttribute('tabindex', '0');
    div.setAttribute('startTime', startTime);
    div.setAttribute('endTime', endTime);
    div.className += ' appt ' + colorClass;
    div.style.width = (fraction * 100) + '%';

    //----Show the duration in the div if requested---
    if(showDuration) {
        div.innerHTML = durationText;
        div.style.color = 'black';
    }
    else div.innerHTML = innertext;

    //----Set content of the pop-up display---
    var description = 'Start Time: '+ StartHour + ':' + StartMinutes +
        '\nEnd Time: ' + EndHour + ':' + EndMinutes +
        '\nDuration: ' + durationText;
    div.setAttribute('data-content', description);
    div.setAttribute('data-html','true');

    cell.appendChild(div);
    return div;
}
/*
   Function: rowSelect

   collapses or expands a pod on the calendar view

   Parameters:

      grouping - a tuple of (ID of pod, number of nurses)  <--todo: question, why do we always send in 4 as the second part of this tuple?

   Returns:

      None

*/
function rowSelect(grouping){
    var groupRow = $('#collapse-row-'+grouping);
    var arrow = document.getElementById('arrow-'+grouping);
    var row = groupRow.next();
    if(arrow.className.indexOf('up') > 0)
        arrow.className = "glyphicon glyphicon-chevron-down";
    else
        arrow.className = "glyphicon glyphicon-chevron-up";

    while(row[0] && !row.hasClass("table-grouper"))
    {
        if(row.is(':hidden'))
            row.show();
        else
            row.hide();
        row = row.next();
    }
}
/*
   Function: getStringDuration

   converts a duration of minutes into a string

   Parameters:

      duration - number of minutes

   Returns:

      durationText - a string  in the format of hours:minutes with an h appended
                    or minutes with an m appended if the duration was less than an hour

*/
function getStringDuration(duration){
    var durationText = "";
    if(duration/60 >= 1){ //if it is longer than an hour
        if(duration%60 > 0) //if the duration has some amount of minutes
            durationText = Math.floor(duration/60) + ':' + duration%60 + 'h';
        else
            durationText = Math.floor(duration/60) + 'h';
    }
    else durationText = duration%60 + 'm';
    return durationText;
}
/*
   Function: MiddleCell

   given two cell indexes, returns the index of cell between the given indices.

   Parameters:

      startCellIndex - the start cell index to look from
      endCellIndex -  the end cell index to look from

   Returns:

      returns index of cell between the given indices

*/
function MiddleCell(startCellIndex, endCellIndex){
    var difference = endCellIndex - startCellIndex;
    if(difference == 0)
        return startCellIndex;
    else if(difference % 2 == 0) //even number
        return startCellIndex + (difference/2)
    else
        return startCellIndex + ((difference - 1)/2)

}

//---------load/save operations of entire schedule--------//
/*
   Function: SaveSchedule

   saves currently displayed schedule to the database

   Parameters:

      overwrite - boolean on whether or not to overwrite an entry of the same name in the database

   Returns:

      none

*/
function SaveSchedule(overwrite){
    var name = $('#SaveName').val();
    var label = $("#pageAlert");
    var alert = document.getElementById("save_alert");
    $('#yesOverwrite').hide();
    $('#noOverwrite').hide();
    $('#save_alert').hide();
    $('#SaveName').attr('readonly','readonly');
    var alreadyExists = CheckSaveName(name);

    if(alreadyExists && overwrite == false) //ask the user if they want to overwrite
    {
        $('#save_alert').show();
        alert.innerHTML = 'That name is already used. Would you like to overwrite it?';
        $('#yesOverwrite').show();
        $('#noOverwrite').show();
        return false;
    }
    else if(alreadyExists && overwrite == true)  //delete so we can overwrite
    {
        if(!DeleteSchedule(name))
        {
            label.css("display", "block");
            label.addClass("alert-danger").removeClass("alert-danger");
            label.text("Unable to save " + name);
            return;
        }
    }
    //Save to DB
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/save_schedule/',
        contentType: "application/json",
        data: {'SaveName': name},
        complete: function(response, textStatus) {
            if(textStatus != 'success') {
                label.text(name + ' could not be saved');
                label.css("display", "block");
                label.addClass("alert-danger").removeClass("alert-success");
            }
            else{
                label.text(name + "has been saved");
                label.css("display", "block");
                label.addClass("alert-success").removeClass("alert-danger");
            }
        }
    });
    $('#saveModal').modal('hide');
}
/*
   Function: CheckSaveName

   checks to see if the name is already attached to a schedule in the database

   Parameters:

      name - name of schedule to be checked

   Returns:

      returnValue - true if the the name is in the database, false otherwise

*/
function CheckSaveName(name){
    var returnValue = false;
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/check_schedule_name/',
        contentType: "application/json",
        data: {'SaveName': name},
        async: false,
        complete: function(response, textStatus) {
            if(textStatus != 'success')
                return alert(textStatus + ': ' + response.responseText);
        },
        success: function(result) {
            if(result == 'True')
                returnValue = true;
            else
                returnValue = false; //unique
        }
    });
    return returnValue;
}
/*
   Function: DeleteSchedule

   deletes schedule of specified name in database

   Parameters:

      name - name of schedule to be deleted

   Returns:

      result - true if the the schedule was successfully deleted from the database, false otherwise

*/
function DeleteSchedule(name){
    var result = false;
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/remove_schedule/',
        contentType: "application/json",
        data: {'SaveName': name},
        async: false,
        complete: function(response, textStatus) {
            if(textStatus != 'success')
                result = false;
            else
                result = true;
        }
    });
    return result;
}