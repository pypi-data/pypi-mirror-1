kukit.actionsGlobalRegistry.register("refreshPage", function(oper) {
    oper.evaluateParameters([], {}, 'refreshPage action');
    window.location.reload();
});
kukit.commandsGlobalRegistry.registerFromAction('refreshPage',
    kukit.cr.makeGlobalCommand);