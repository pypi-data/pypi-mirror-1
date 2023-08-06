

/* Base kukit plugins for plonearticle*/

/* innercontainers edit forms */
kukit.actionsGlobalRegistry.register("plone-initPloneArticleEditWidget", function(oper) {
    oper.evaluateParameters([], {}, 'plone-initPloneArticleEditWidget action'); 
    kukit.log('Load the PloneArticle Edit Widget inline');    
    Field_init(oper.node);
    kukit.logDebug('PloneArticle Edit Widget loaded.'); 
});

kukit.commandsGlobalRegistry.registerFromAction('plone-initPloneArticleEditWidget', 
    kukit.cr.makeSelectorCommand);

/* relaod models javascripts when reloading pa_content */

kukit.actionsGlobalRegistry.register("plone-initPloneArticleView", function(oper) {
    oper.evaluateParameters([], {}, 'plone-initPloneArticleView action'); 
    kukit.logDebug('Load PloneArticle Content.'); 
    kukit.log('Load the PloneArticle Models methods');     
    jQuery(document).ready(pamodel.__init__);
    kukit.logDebug('PloneArticle Content loaded.'); 
});

kukit.commandsGlobalRegistry.registerFromAction('plone-initPloneArticleView', 
    kukit.cr.makeSelectorCommand);
