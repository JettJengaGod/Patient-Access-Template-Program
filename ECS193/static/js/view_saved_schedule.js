
function button_delete_click(name){
    var label = $("#pageAlert");
    if(DeleteSchedule(name)){ //located in calendar.js
        label.text('\'' + name + '\'' + ' has been deleted');
        label.css("display", "block");
        label.addClass("alert-success").removeClass("alert-danger");
        $('#row-'+name).hide();
    }
    else {
        label.text('An error has occurred when attempting to delete \'' + name + '\'');
        label.css("display", "block");
        label.addClass("alert-danger").removeClass("alert-success");
    }
}