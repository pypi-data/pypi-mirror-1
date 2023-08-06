function showRestart(id) {
    new Ajax.Updater(
            id,
            '/admin/show_restart',
            {asynchronous:true, evalScripts:true}
        );
}

function startReceiver() {
    showRestart('receiverStatus');
    new Ajax.Updater(
            'receiverStatus',
            '/admin/start_receiver',
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

function showStatusReceiver() {
    new Ajax.Updater(
            'receiverStatus',
            '/admin/show_status_receiver',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

