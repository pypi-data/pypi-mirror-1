kukit.actionsGlobalRegistry.register("resizePanel", function(oper) {
    /* Resize the GloWorm panel to fit its contents.
       TODO: Right now, the extral 35 pixels are completely arbitrary, figure out a better value.
    */
    newHeight = document.getElementById('glowormPanelBody').offsetHeight + 35;
    document.getElementById('glowormPanel').style.height = newHeight;
    document.getElementById('glowormPageWrapper').style.bottom = newHeight;
});
kukit.commandsGlobalRegistry.registerFromAction('resizePanel',
    kukit.cr.makeGlobalCommand);