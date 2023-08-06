<!--

var bg_select = "#95e0c8"

function show_contacts(field) {
    new Ajax.Updater('contactList', 'show_contacts?recipient='+field.value, {asynchronous:true, evalScripts:true});
    return false;
}

function add_rem(me, field, num) {
    new Ajax.Updater('recipientField', 'add_rem_num?number='+num+'&recipient='+field.value, {asynchronous:true, evalScripts:true});
    return false;
}

//-->
