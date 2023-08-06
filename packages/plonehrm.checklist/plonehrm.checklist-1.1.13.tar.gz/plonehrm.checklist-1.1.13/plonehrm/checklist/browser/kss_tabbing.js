/* This file declares runs the form tabbing script from plone as a 
KSS client-action.
This is needed when you load a page wich is supposed to be tabbed with KSS,
the Javascript code is not executed anymore and you just get fieldsets.

See 'Products/CMFPlone/skins/plone_ecmascript/form_tabbing.js' for the
real tabbing code.
*/

kukit.actionsGlobalRegistry.register("kss-tabbing", function(oper) {
    oper.completeParms([], {}, 'ksstutorial-demoplugin action');

    /*var date = new Date();
    var curDate = null;
    
    do { curDate = new Date(); }
    while(curDate-date < 5000);*/

    jq("form.enableFormTabbing,div.enableFormTabbing")
        .each(ploneFormTabbing.initializeForm);
    jq("dl.enableFormTabbing").each(ploneFormTabbing.initializeDL);
});

kukit.commandsGlobalRegistry.registerFromAction('kss-tabbing', 
                                                kukit.cr.makeSelectorCommand);