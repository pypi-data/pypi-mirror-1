kukit.actionsGlobalRegistry.register("initializeBlogView", function(oper) {
    oper.evaluateParameters(['anchor'], {}, "initializeBlogView action");
    
    var anchorstring = oper.parms.anchor;
    
    if (!anchorstring) {
    	var url = String(document.location);
	    var anchorindex = url.indexOf('#');
    	if (anchorindex != -1) {
    		var anchorstring = url.substring(anchorindex + 1, url.length);
		    var queryindex = anchorstring.indexOf('?');
		    if (queryindex != -1) {
		    	anchorstring = anchorstring.substring(0, queryindex);
		    }
    	}
    }
    
    if (anchorstring) {
    	var element;
		$('.discussion').each(function() {
			element = $('a[name=' + anchorstring + ']', this).get(0);
			if (!element) {
				toggleComments(this.id);
			}
		});
    } else {
		$('.replytitle').toggleClass('commentsopen');
		$('.discussion').toggleClass('hiddenComments');
	}
    
});
kukit.commandsGlobalRegistry.registerFromAction('initializeBlogView',
                                                kukit.cr.makeGlobalCommand);