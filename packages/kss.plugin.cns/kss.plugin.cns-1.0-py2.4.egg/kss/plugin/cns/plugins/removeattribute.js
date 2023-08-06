kukit.actionsGlobalRegistry.register("removeAttribute", function(oper) {
    oper.evaluateParameters(['name'],{}, 'removeAttribute action');
    /* Sets value ot target element by either source_element value or directly value
     * Either source_element or value has to be given
     */

   try {
       oper.node.removeAttribute(oper.parms.name)
   }
   catch (err) {;}
   
});
kukit.commandsGlobalRegistry.registerFromAction('removeAttribute',
    kukit.cr.makeSelectorCommand);