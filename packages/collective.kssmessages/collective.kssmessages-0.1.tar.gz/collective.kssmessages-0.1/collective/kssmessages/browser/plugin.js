kukit.actionsGlobalRegistry.register("kssmessages-error", function(oper) {
    // There is nothing in oper which indicates a timeout directly
    // but we can infer a timeout by looking at the expiry time.
    now = (new Date()).valueOf();
    if (now > oper.queueItem.expire)
    {
        var came_from = escape(window.location.href);
        jq.get('@@kssmessages.timeout-page?came_from='+came_from, function(data){
            kssmessages.popupShow(data);
        });
    }
    else
    {
        msg = 'Other error. To be implemented.'
        kssmessages.popupShow(data);
    }
});

kukit.commandsGlobalRegistry.registerFromAction('kssmessages-error', kukit.cr.makeSelectorCommand);
