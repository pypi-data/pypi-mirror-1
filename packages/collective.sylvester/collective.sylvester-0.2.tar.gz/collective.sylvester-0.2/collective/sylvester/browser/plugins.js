kukit.actionsGlobalRegistry.register("collective.sylvester.dashboard-error", function (oper) {
    oper.evaluateParameters([], {}, 'collective.sylvester.dashboard-error action');

    var button = oper.node;

    var div = document.getElementById('collective-sylvester-dashboard-messages');
    // xxx: translation?
    if (div)
        div.innerHTML = '<dl class="portalMessage error"><dt>Error</dt><dd>The server is taking too long to respond. Please try again.</dd></dl>';

    // Enable the button
    button.disabled = false;
    jq(button).removeClass('submitting');

    var form = new kukit.fo.CurrentFormLocator(button).getForm();
    // Fade in
    jq(form).fadeTo('fast', 1.0)    

});
kukit.commandsGlobalRegistry.registerFromAction('collective.sylvester.dashboard-error',
    kukit.cr.makeSelectorCommand)

kukit.actionsGlobalRegistry.register("collective.sylvester.disable-form", function (oper) {
    oper.evaluateParameters([], {}, 'collective.sylvester.disable-form action');

    var button = oper.node;

    // Disable button   
    button.disabled = true;

    // Clear messages    
    var div = document.getElementById('collective-sylvester-dashboard-messages');
    if (div)
    {
        div.innerHTML = '';
        jq(div).removeClass('error');
    }

    // todo: use jquery to disable all form elements
    var form = new kukit.fo.CurrentFormLocator(button).getForm();
    // Fade out
    jq(form).fadeTo('fast', 0.4)    
});
kukit.commandsGlobalRegistry.registerFromAction('collective.sylvester.disable-form',
    kukit.cr.makeSelectorCommand)

// An action that does nothing
kukit.actionsGlobalRegistry.register("collective.sylvester.pass", function (oper) {
    oper.evaluateParameters([], {}, 'collective.sylvester.pass action');
});
kukit.commandsGlobalRegistry.registerFromAction('collective.sylvester.pass',
    kukit.cr.makeSelectorCommand)
