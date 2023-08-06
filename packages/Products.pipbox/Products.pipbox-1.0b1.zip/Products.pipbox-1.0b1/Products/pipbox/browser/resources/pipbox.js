/*****************

   PIPbox tools for attaching JQuery Tools bling to CSS with option
   parameter strings.
   
   This uses overlayhelpers.js in plone.app.jquerytools for most of
   the real work.

*****************/


/******
    pb.doSetup
    parameter: an options object(p)
    options vary by type and subtype of bling.
******/
pb.doSetup = function(p) {
    switch (p.type) {
    case 'overlay':
        jQuery(function() {
            jQuery(p.selector).prepOverlay(p);
        });
        break;
    case 'tabs':
        jQuery(function() {
            var config = p.config || {};
            config.tabs = p.tabs || config.tabs || 'a';
            jQuery(p.tabcontainer).addClass('pbactive').tabs(p.panes, config);
            jQuery(p.panes).addClass('pbactive');
        });
        break;
    }
};


/******
    pb.doConfig
    parameter: a config object(s)
    for JQ Tools global configuration
******/
pb.doConfig = function(p) {
    var tools = jQuery.tools;
    var tool = p.tool;

    if (tool) {
        for (var key in p) {
            if (key != 'tool') {
                tools[tool].conf[key] = p[key];
            }
        }
    }
};
