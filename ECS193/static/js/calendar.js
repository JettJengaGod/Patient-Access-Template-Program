

function BuildRNRow(count, chairs, startTime, lunchTime, duration, endTime) {
    var table = document.getElementById("calendar");
    var firstRow = true; //first row of each RN group has 1 extra cell for the pod group - need to track
    for(var i=count*chairs+1; i < (count+1)*chairs+1; i++)
    {
        if(firstRow) var offset = 7; else var offset = 8;
        var row = table.rows[i];

        //block out times before nurse arrives
        var startTimeCell = row.cells[startTime.split(':')[0]-offset];
        var startTimePercent = (startTime.split(':')[1])/60;
        if(firstRow) var j = 1; else var j = 0;
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
        if(firstRow) var maxCells = 10; else var maxCells = 9;
        while (endTimeIndex++ < maxCells)
            AddFill(row.cells[endTimeIndex],1,'unavailable',true);

        firstRow = false;
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
