

function BuildRNRow(RNIndex, startTime, lunchTime, duration, endTime) {
    var table = document.getElementById("calendar");
    var maxCellIndex = 9;
    var offset = 8; //used to calculate row index from given hour
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
function AddAppointment(RNIndex, chairIndex, startTime, endTime, apptID) {
    var row = document.getElementById("RN-"+RNIndex+"-row-"+chairIndex);
    var offset = 8;

    var startIndex = startTime.split(':')[0] - offset;
    var startMinutes = parseInt(startTime.split(':')[1]);
    var startPercent = startMinutes/60;
    var endIndex = endTime.split(':')[0] - offset;
    var endMinutes = parseInt(endTime.split(':')[1]);
    var endPercent = endMinutes/60;
    var totalTime = (endIndex*60 + endMinutes) - (startIndex*60 + startMinutes);
    var DurationCell = row.cells[MiddleCell(startIndex, endIndex)]; //The cell to put the duration name in

    var color = RandomColor();

    // appointment doesn't start on the hour
    if (startMinutes > 0) {
        //right shift
        if (startIndex != endIndex) {
            var cell = row.cells[startIndex++];
            BuildApptDiv(cell, 1 - startPercent, false, cell == DurationCell, color, apptID, startTime, endTime);
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
            BuildApptDiv(cell, (endPercent - startPercent), true, cell == DurationCell, color, apptID, startTime, endTime);
            totalTime = 0;
            endMinutes = 0;
        }
    }
    // appointment doesn't end on the hour
    if (endMinutes > 0) {
        var cell = row.cells[endIndex];
        BuildApptDiv(cell, endPercent, true, cell == DurationCell, color, apptID, startTime, endTime);
        totalTime -= endMinutes;
    }
    // fills out entire hour slot
    while (totalTime > 0) {
        var cell = row.cells[startIndex++];
        BuildApptDiv(cell, 1, true, cell == DurationCell, color, apptID, startTime, endTime);
        totalTime -= 60;
    }
    lastEndIndex = endIndex;
    lastEndPercent = endPercent;
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
    cell.appendChild(div);
    div.className += ' ' + className;
    div.style.width = (fraction * 100) + '%';
}

function BuildApptDiv(cell, fraction, leftAligned, showDuration, color, id, startTime, endTime)
{
    if(fraction > 1 || fraction < 0)
    {
        alert("The given fraction to fill the cell by is not a valid percent!")
        return;
    }

    cell.style.padding = 0;
    var div = document.createElement('a');

    if (!leftAligned)
        div.style.float = 'right';
    var innertext = '&nbsp;';
    div.style.backgroundColor = color;
    div.style.color = color;
    div.id = id;
    div.className += ' appt-' + id;
    div.setAttribute('role', 'button');
    div.setAttribute('data-toggle', 'popover');
    div.setAttribute('data-trigger', 'focus');
    div.setAttribute('data-placement', 'top');
    div.setAttribute('tabindex', '0');
    div.className += ' appt';
    div.style.width = (fraction * 100) + '%';

    //----calculate the duration of entire appointment in hours and minutes---
    var durationText = "";
    var duration = (endTime.split(':')[0] - startTime.split(':')[0])*60  + (endTime.split(':')[1] - startTime.split(':')[1]);
    if(duration/60 > 1){ //if it is longer than an hour
        if(duration%60 > 0) //if the duration has some amount of minutes
            durationText = Math.floor(duration/60) + '.' + duration%60 + 'h';
        else
            durationText = Math.floor(duration/60) + 'h';
    }
    else durationText = duration%60 + 'm';

    //----Show the duration in the div if requested---
    if(showDuration) {
        div.innerHTML = durationText;
        div.style.color = 'black';
    }
    else div.innerHTML = innertext;

    //----Set content of the pop-up display---
    var description = 'Start Time: '+startTime +
        '\nEnd Time: ' + endTime +
        '\nDuration: ' + durationText;
    div.setAttribute('data-content', description);

    cell.appendChild(div);
}

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

function RandomColor(){
    var x=Math.round(0xffffff * Math.random()).toString(16);
    var y=(6-x.length);
    var z= '000000';
    var z1 = z.substring(0,y);
    var color = '#' + z1 + x;
    return(color);
}

function MiddleCell(startCellIndex, endCellIndex){
    var difference = endCellIndex - startCellIndex;
    if(difference == 0)
        return startCellIndex;
    else if(difference % 2 == 0) //even number
        return startCellIndex + (difference/2)
    else
        return startCellIndex + ((difference - 1)/2)

}
