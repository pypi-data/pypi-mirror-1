kukit.actionsGlobalRegistry.register("openWindow", function(oper) {
    oper.evaluateParameters(['url'],{}, 'openWindow action');
    /* Shows alert box with a given message ( not for debugging purposes as core alert plugin)
     */
    
   window.open(oper.parms.url)
});
kukit.commandsGlobalRegistry.registerFromAction('openWindow',
    kukit.cr.makeGlobalCommand);