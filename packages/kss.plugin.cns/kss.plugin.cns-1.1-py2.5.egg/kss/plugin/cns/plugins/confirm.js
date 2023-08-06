// thanks Balasz Ree for providing example of this code.

kukit.actionsGlobalRegistry.register("cns-confirm", 
    function(oper) {
    oper.evaluateParameters(['text'], {}, 'confirm action');
    // Find the binderInstance of the switcher.
    // (since we are in an action and not in the event,
    // we don't have it at hand.
    // Note that we would not necessarily need the singleton)
    var binderInfo =
        kukit.engine.binderInfoRegistry.getSingletonBinderInfoByName('cns',
        'confirmed');
    var binder = binderInfo.getBinder();
    // We do the popup only if there is a message.
    var result = true;
    if (oper.parms.text) {
        result = confirm(oper.parms.text);
    }
    // arrange the continuation events
    if (result) {
        // XXX XXX in a following kss version you will need to change
        // this with the full namespaced name!!!
        // Continue with the real action.
        //var name = 'cns-confirmed';
        var name = 'confirmed';
    } else {
        // Continue with the cancel action.
        // var name = 'cns-nothanks';
        var name = 'nothanks';
    }
    binder.continueEvent(name, oper.node, {});
});

kukit.commandsGlobalRegistry.registerFromAction('cns-confirm',
    kukit.cr.makeSelectorCommand);

var _conditionalEvents = function() {

    this.__default_failed__ = 
        function(name, oper) {};

};

kukit.eventsGlobalRegistry.register('cns', 'confirmed',
    _conditionalEvents, null, null);

kukit.eventsGlobalRegistry.register('cns', 'nothanks',
    _conditionalEvents, null, '__default_failed__');

