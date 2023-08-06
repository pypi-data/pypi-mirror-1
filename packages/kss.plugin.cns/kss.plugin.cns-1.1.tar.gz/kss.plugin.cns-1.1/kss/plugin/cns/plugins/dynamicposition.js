/* Set the object into specified place in window no matter on scrollig   - IE 6 fix */
kukit.actionsGlobalRegistry.register("dynamicPosition", function(oper) {
    oper.evaluateParameters(['left', 'top'], {}, 'dynamicPosition action');
    
    dp_dynamicPosition(oper.parms.left, oper.parms.top, oper.node);
    
});
kukit.commandsGlobalRegistry.registerFromAction('dynamicPosition',
    kukit.cr.makeGlobalCommand);
    
function dp_dynamicPosition(left, top, node) {
    left = dp_parsePosition(left, 'left', node);
    top = dp_parsePosition(top, 'top', node);
    
    newleft = dp_correctPosition(node, left, 'Left');
    newtop = dp_correctPosition(node, top, 'Top');
    
    node.style['position'] = "absolute";
    node.style['left'] = parseInt(newleft)+ "px";
    node.style['top'] = parseInt(newtop)+ "px";
}
    
function dp_parsePosition(position, type, node) {
    if (position == "center") { 
        if (type == "left") {
            pos = parseInt(document.documentElement.clientWidth / 2 - node.clientWidth / 2);
        } else {
            pos = parseInt(document.documentElement.clientHeight / 2 - node.clientHeight / 2);
        }
    } else {
        pos = parseInt(position);
    }
    return (pos);
};

function dp_correctPosition(oElement,oPos,oWhich) {
  oPos += document.documentElement['scroll'+oWhich] ? parseInt(document.documentElement['scroll'+oWhich]) : parseInt(document.body['scroll'+oWhich]);
  return oPos;
};