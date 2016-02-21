

function BuildRNRow(RNIndex, chairs, startTime, lunchTime, duration, endTime) {
    var table = document.getElementById("calendar");
    var maxCells = 9;
    var offset = 8; //used to calculate row index from given hour
    //RN number 'RNIndex' is responsible for 'chairs' number of chairs => this rn has 'chairs' + 1 total rows
    //Each RN row group has a hidden row that is used to collapse/un-collapse the group
    //Must not forget that table.rows[0] is the header
    for(var i=RNIndex*chairs+2+RNIndex; i < (RNIndex+1)*chairs+2+RNIndex; i++)
    {
        var row = table.rows[i];

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
        while (endTimeIndex++ < maxCells)
            AddFill(row.cells[endTimeIndex],1,'unavailable',true);
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

function rowSelect(nurseIndex, chairs){
    var rowGroup = document.getElementById("row-group-"+nurseIndex).cells[0];
    var hiddenRow = $('#collapse-row-'+nurseIndex);
    if(hiddenRow.is(':hidden'))
    {
        hiddenRow.show();
        for(var i = 1; i <= chairs; i++)
        {
            var row = $('#RN-'+nurseIndex+'-row-'+i);
            row.hide();
        }
        rowGroup.rowSpan = 1;
    }
    else
    {
        hiddenRow.hide();
        rowGroup.rowSpan = chairs + 1;
        for(var i = 1; i <= chairs; i++)
        {
            var row = $('#RN-'+nurseIndex+'-row-'+i);
            row.show();
        }
    }
}
