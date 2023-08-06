kukit.actionsGlobalRegistry.register("redirectRequest", function(oper) {
    oper.evaluateParameters(['url'], {}, 'redirectRequest action');
    window.location.replace(oper.parms.url);
});
kukit.commandsGlobalRegistry.registerFromAction('redirectRequest',
    kukit.cr.makeGlobalCommand);