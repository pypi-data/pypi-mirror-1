kukit.actionsGlobalRegistry.register('addImages', function(oper) {
;;; oper.componentName = '[addImages] action';
    var images = jq(eval(oper.parms.images));
    if(oper.parms.doneLoading == "True"){
        //should stop anymore ajax call attempts
        document.trueGallery.doneLoading = true;
    }else{
        document.trueGallery.addAll(images);
        jq('div#plone-true-gallery').removeClass('kssattr-imagePage-' + oper.parms.page);
        jq('div#plone-true-gallery').addClass('kssattr-imagePage-' + (parseInt(oper.parms.page)+1));
    }
});

kukit.commandsGlobalRegistry.registerFromAction('addImages',
    kukit.cr.makeSelectorCommand);
