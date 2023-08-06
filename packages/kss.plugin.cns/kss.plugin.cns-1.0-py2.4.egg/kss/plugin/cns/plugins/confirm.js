kukit.actionsGlobalRegistry.register("confirm", function(oper) {
	oper.evaluateParameters(['text'], {}, 'confirm action');
	
	if (confirm(oper.parms.text)) {
        oper.binderInstance.__continueEvent__('confirmed', oper.node, {});
	};
});
kukit.commandsGlobalRegistry.registerFromAction('confirm', 
                                                kukit.cr.makeSelectorCommand);

      
kukit.eventsGlobalRegistry.register(null, 'confirmed', kukit.pl.NativeEventBinder, null, null);