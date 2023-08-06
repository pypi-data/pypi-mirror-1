kukit.actionsGlobalRegistry.register("alertText", function(oper) {
    oper.evaluateParameters(['message'],{}, 'alertText action');
    /* Shows alert box with a given message ( not for debugging purposes as core alert plugin)
     */
    
   alert(oper.parms.message)
});
kukit.commandsGlobalRegistry.registerFromAction('alertText',
    kukit.cr.makeGlobalCommand);