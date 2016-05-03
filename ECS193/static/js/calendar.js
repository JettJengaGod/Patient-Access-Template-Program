
//Color when nurses are available and are gone
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
        if(endTimePercent == 0)
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

function Reserve(apptID){
    $('.appt-'+apptID).each(function () {
        var x = $(this);
        x.addClass("appt-reserved");
        var str = "<br><span style='color: orange'>USER RESERVED</span>";
        x.attr('data-content', x.attr('data-content')+str);
    });
}

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

//similar to function AddFill except with appointment only attributes
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
    var color = GetColor(minutes);
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
    div.style.backgroundColor = color;
    div.style.color = color;
    div.className += ' appt-' + id;
    div.setAttribute('role', 'button');
    div.setAttribute('data-toggle', 'popover');
    div.setAttribute('data-trigger', 'focus');
    div.setAttribute('data-placement', 'top');
    div.setAttribute('tabindex', '0');
    div.className += ' appt';
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

//Collapse/expand a pod
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

function GetColor(duration){
    switch(duration){
        case 30:
            return "#ff8080";
        case 45:
            return "#ff80ff";
        case 60:
            return "#bf80ff";
        case 90:
            return "#9f80ff";
        case 120:
            return "#809fff";
        case 150:
            return "#80dfff";
        case 180:
            return "#80ffdf";
        case 210:
            return "#80ff9f";
        case 240:
            return "#80ff80";
        case 270:
            return "#9fff80";
        case 300:
            return "#bfff80";
        case 330:
            return "#dfff80";
        case 360:
            return "#ffff80";
        case 390:
            return "#ffdf80";
        case 420:
            return "#ffbf80";
        case 450:
            return "#ff9f80";
        case 480:
            return "#ff8080";
        default:
            return "#dcb6a3";
    }
}

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

//returns index of cell between the given indices.
function MiddleCell(startCellIndex, endCellIndex){
    var difference = endCellIndex - startCellIndex;
    if(difference == 0)
        return startCellIndex;
    else if(difference % 2 == 0) //even number
        return startCellIndex + (difference/2)
    else
        return startCellIndex + ((difference - 1)/2)

}

//-----load/save operations of entire schedule-----//
function SaveSchedule(overwrite){
    var name = $('#SaveName').val();
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
        DeleteSchedule(name);
    }
    //Save to DB
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/save_schedule/',
        contentType: "application/json",
        data: {'SaveName': name},
        success: function(result) {
            var label = $("#pageAlert");
            label.text(result);
            label.css("display", "block");
            label.addClass("alert-success").removeClass("alert-danger");
            $('#saveSchedule').disable();
        },
        complete: function(response, textStatus) {
            if(textStatus != 'success') {
                var label = $("#pageAlert");
                label.text(name + ' could not be saved');
                label.css("display", "block");
                label.addClass("alert-danger").removeClass("alert-success");
            }
        }
    });
    $('#saveModal').modal('hide');
}

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
                returnValue = false; //unique
            else
                returnValue = true; //already used
        }
    });
    return returnValue;
}

function DeleteSchedule(name){
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/remove_schedule/',
        contentType: "application/json",
        data: {'SaveName': name},
        async: false,
        complete: function(response, textStatus) {
            if(textStatus != 'success')
                return false;
        },
        success: function() {
            return true;
        }
    });
    return true;
}