kukit.actionsGlobalRegistry.register("kssinline-popupShow", function(oper) {
    oper.evaluateParameters(['dom_node_id'], {}, 'kssinline-popupShow action');
    var dom_node_id = oper.parms.dom_node_id;
    corePopupShow(dom_node_id);
});

kukit.actionsGlobalRegistry.register("kssinline-popupHide", function(oper) {
    oper.evaluateParameters([], {}, 'kssinline-popupHide action');
    corePopupHide();
});

kukit.actionsGlobalRegistry.register("kssinline-redirect", function(oper) {
    oper.evaluateParameters(['url'], {}, 'kssinline-redirect action');
    var url = oper.parms.url;
    window.location.href = url;
})
;
kukit.actionsGlobalRegistry.register("kssinline-fadeout", function(oper) {
    oper.evaluateParameters([], {}, 'kssinline-fadeout action');
    jq('#visual-portal-wrapper').fadeTo('fast', 0.4);
});

kukit.actionsGlobalRegistry.register("kssinline-followLink", function(oper) {
    oper.evaluateParameters([], {}, 'kssinline-followLink action');
    // If the node foes not have an attribute href then search upwards
    // in the DOM until a node with an href is found.
    var node = oper.node;
    if (!node.getAttribute('href'))
        node = node.parentNode;
    var url = node.href;
    if (url.substr(0, 7) == "http://") {
        // redirect to it
        window.location.replace(url);
    } else if (url.substr(0, 13) == "javascript://") {
        // execute it
        eval(url.substr(13));
    }   
});

kukit.commandsGlobalRegistry.registerFromAction('kssinline-popupShow', kukit.cr.makeSelectorCommand);
kukit.commandsGlobalRegistry.registerFromAction('kssinline-popupHide', kukit.cr.makeSelectorCommand);
kukit.commandsGlobalRegistry.registerFromAction('kssinline-redirect', kukit.cr.makeSelectorCommand);
kukit.commandsGlobalRegistry.registerFromAction('kssinline-fadeout', kukit.cr.makeSelectorCommand);
kukit.commandsGlobalRegistry.registerFromAction('kssinline-followLink', kukit.cr.makeSelectorCommand);
