

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
            AddFill(row.cells[++endTimeIndex],1,'unavailable',true);
        else if(endTimePercent > 0)
            AddFill(row.cells[++endTimeIndex],1 - endTimePercent,'unavailable',false);
        while (endTimeIndex++ < maxCellIndex)
            AddFill(row.cells[endTimeIndex],1,'unavailable',true);

        i++;
        row = document.getElementById("RN-"+RNIndex+"-row-"+i);
    }
}

var lastEndIndex = 0;
var lastEndPercent = 0;
function AddAppointment(RNIndex, chairIndex, startTime, endTime) {
    var row = document.getElementById("RN-"+RNIndex+"-row-"+chairIndex);
    var offset = 8;

    var startIndex = startTime.split(':')[0] - offset;
    var startMinutes = parseInt(startTime.split(':')[1]);
    var startPercent = startMinutes/60;
    var endIndex = endTime.split(':')[0] - offset;
    var endMinutes = parseInt(endTime.split(':')[1]);
    var endPercent = endMinutes/60;
    var totalTime = (endIndex*60 + endMinutes) - (startIndex*60 + startMinutes);

    var color = RandomColor();

    // appointment doesn't start on the hour
    if (startMinutes > 0) {
        //right shift
        if (startIndex != endIndex) {
            AddFill(row.cells[startIndex++], 1 - startPercent, 'appt', false, color);
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
            AddFill(row.cells[startIndex], (endPercent - startPercent), 'appt', true, color);
            totalTime = 0;
            endMinutes = 0;
        }
    }
    // appointment doesn't end on the hour
    if (endMinutes > 0) {
        AddFill(row.cells[endIndex], endPercent, 'appt', true, color);
        totalTime -= endMinutes;
    }
    // fills out entire hour slot
    while (totalTime > 0) {
        AddFill(row.cells[startIndex++], 1, 'appt', false, color);
        totalTime -= 60;
    }
    lastEndIndex = endIndex;
    lastEndPercent = endPercent;
}

function AddFill(cell, fraction, className, leftAligned, color){
    if(fraction > 1 || fraction < 0)
    {
        alert("The given fraction to fill the cell by is not a valid percent!")
        return;
    }

    cell.style.padding = 0;
    var div = document.createElement('div');
    div.innerHTML = '&nbsp;';
    cell.appendChild(div);
    div.className += ' ' + className;
    div.style.width = (fraction * 100) + '%';
    div.style.display = 'inline-block';
    div.style.backgroundColor = color;
    if(!leftAligned)
        div.style.float = 'right';
}

function rowSelect(grouping){
    var groupRow = $('#collapse-row-'+grouping);
    var row = groupRow.next();
    while(row[0] && !row.hasClass("table-grouper"))
    {
        if(row.is(':hidden'))
            row.show();
        else
            row.hide();
        row = row.next();
    }
}

function RandomColor()
{
    var x=Math.round(0xffffff * Math.random()).toString(16);
    var y=(6-x.length);
    var z= '000000';
    var z1 = z.substring(0,y);
    var color = '#' + z1 + x;
    return(color);
}
