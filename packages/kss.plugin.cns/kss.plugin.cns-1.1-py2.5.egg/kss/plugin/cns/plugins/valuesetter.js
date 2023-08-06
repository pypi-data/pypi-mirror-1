kukit.actionsGlobalRegistry.register("valueSetter", function(oper) {
    oper.evaluateParameters(['target_element'], {'source_element':null,'value':null, 'attribute':'value','condition_element':null, 'condition_attribute':'value', 'condition_value':null}, 'valueSetter action');
    /* Sets value ot target element by either source_element value or directly value
     * Either source_element or value has to be given
     */
    
    if (oper.parms.value == null && oper.parms.source_element == null)
        return;

    if (oper.parms.condition_element != null) {
        cond_elem = document.getElementById(oper.parms.condition_element);
        if (! Boolean(cond_elem[oper.parms.condition_attribute])) {
            if (oper.parms.condition_value != null)
                document.getElementById(oper.parms.target_element)[oper.parms.attribute] = oper.parms.condition_value;
            return
        }
    }
    
    if (oper.parms.source_element != null)
        value = document.getElementById(oper.parms.source_element).value;
    else
        value = oper.parms.value;
    
    if (oper.parms.attribute == "checked")
        value = Boolean(eval(value));
        
    document.getElementById(oper.parms.target_element)[oper.parms.attribute] = value;
});
kukit.commandsGlobalRegistry.registerFromAction('valueSetter',
    kukit.cr.makeGlobalCommand);