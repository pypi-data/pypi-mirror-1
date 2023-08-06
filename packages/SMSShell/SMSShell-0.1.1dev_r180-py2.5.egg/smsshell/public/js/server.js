function showRestart(id) {
    new Ajax.Updater(
            id,
            '/admin/show_restart',
            {asynchronous:true, evalScripts:true}
        );
}

function startReciever() {
    showRestart('recieverStatus');
    new Ajax.Updater(
            'recieverStatus',
            '/admin/start_reciever',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

function startSender() {
    showRestart('senderStatus');
    new Ajax.Updater(
            'senderStatus',
            '/admin/start_sender',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

function showStatus() {
    window.location.reload(true);
    return false;
}

function showStatusSender() {
    new Ajax.Updater(
            'senderStatus',
            '/admin/show_status_sender',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

function showStatusReciever() {
    new Ajax.Updater(
            'recieverStatus',
            '/admin/show_status_reciever',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

