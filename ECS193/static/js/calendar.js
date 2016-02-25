

function BuildRNRow(RNIndex, startTime, lunchTime, duration, endTime) {
    var table = document.getElementById("calendar");
    var maxCellIndex = 9;
    var offset = 8; //used to calculate row index from given hour
    var i = 1;

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
        var lunchTimeOffset = parseInt(lunchTime.split(':')[1]);
        var lunchTimePercent = (duration-lunchTimeOffset)/60;
        if(lunchTimeOffset > 0)
            AddFill(row.cells[LunchIndex++],1 - lunchTimeOffset/60,'lunch',false);
        while(lunchTimePercent >= 1) { //if the total lunch duration is greater than 60 minutes
            AddFill(row.cells[LunchIndex++],1,'lunch',true);
            lunchTimePercent--;
        }
        if(lunchTimePercent > 0)
            AddFill(row.cells[LunchIndex],lunchTimePercent,'lunch',true);

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
function AddFill(cell, fraction, className, leftAligned){
    cell.style.padding = 0;
    var div = document.createElement('div');
    div.innerHTML = '&nbsp;';
    cell.appendChild(div);
    div.className += ' ' + className;
    div.style.width = (fraction * 100) + '%';
    if(!leftAligned)
    {
        div.style.float = 'right';
    }
}

function rowSelect(grouping, chairs){
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
