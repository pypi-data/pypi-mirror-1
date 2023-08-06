/* 'Lightbox Gone Wild' by: Chris Campbell (http://particletree.com)
   Adapted by Netsight for Plone via KSS
*/

LightboxUtils = {};
LightboxVars = {};

/* IE requires height to 100% and overflow hidden 
otherwise you can scroll down past the lightbox */
LightboxUtils.prepareIE = function(height, overflow){
    bod = document.getElementsByTagName('body')[0];
    bod.style.height = height;
    bod.style.overflow = overflow;
    
    htm = document.getElementsByTagName('html')[0];
    htm.style.height = height;
    htm.style.overflow = overflow; 
};
	
// In IE, select elements hover on top of the lightbox
LightboxUtils.hideSelects = function(visibility){
    selects = document.getElementsByTagName('select');
    for(i = 0; i < selects.length; i++) {
	selects[i].style.visibility = visibility;
    }
};
	
LightboxUtils.getScroll = function(){
    if (self.pageYOffset) {
	LightboxVars.yPos = self.pageYOffset;
    } else if (document.documentElement && document.documentElement.scrollTop){
	LightboxVars.yPos = document.documentElement.scrollTop; 
    } else if (document.body) {
	LightboxVars.yPos = document.body.scrollTop;
    }
};
	
LightboxUtils.setScroll = function(x, y){
    window.scrollTo(x, y); 
};

/* Initialize browser detection stuff */
kukit.actionsGlobalRegistry.register("lightboxing-initialize", function() {
    function checkIt(string) {
	place = detect.indexOf(string) + 1;
	thestring = string;
	return place;
    }
    var detect = navigator.userAgent.toLowerCase();
    if (checkIt('msie')) LightboxVars.browser 	= "Internet Explorer"
    else if (!checkIt('compatible')) {
	LightboxVars.browser = "Netscape Navigator"
	LightboxVars.version = detect.charAt(8);
    }
    else LightboxVars.browser = "An unknown browser";

    if (!LightboxVars.version) {
	LightboxVars.version = detect.charAt(place + thestring.length);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('lightboxing-initialize', 
                                                kukit.cr.makeSelectorCommand);

/* Add the markup */
kukit.actionsGlobalRegistry.register("lightboxing-addMarkup", function() {

    /* Add markup if necessary */
    if (!document.getElementById('lightbox')) {
	bod = document.getElementsByTagName('body')[0];
	overlay = document.createElement('div');
	overlay.id = 'overlay';
	lb = document.createElement('div');
	lb.id = 'lightbox';
	lb.className = 'loading';
	
	bod.appendChild(overlay);
	bod.appendChild(lb);

	closer = document.createElement('div');
	closer.id = 'lbCloser';
	bod.appendChild(closer);
    };
    
    if (LightboxVars.browser == 'Internet Explorer' 
	&& LightboxVars.version != '7') {
	LightboxUtils.getScroll();
	LightboxUtils.prepareIE('100%', 'hidden');
	LightboxUtils.setScroll(0,0);
	LightboxUtils.hideSelects('hidden');
    }

    /* Loading */
    document.getElementById('lightbox').innerHTML = '<div id="lbInner" class="documentContent"><div id="lbContent"><p>Loading</p></div></div>';
    /* Show lightbox */
    var lbparts = ['overlay', 'lightbox', 'lbCloser'];
    for (i=0; i<lbparts.length; i++) {
	document.getElementById(lbparts[i]).style.display = 'block';
    }
});
kukit.commandsGlobalRegistry.registerFromAction('lightboxing-addMarkup', 
                                                kukit.cr.makeSelectorCommand);

/* Close the lightbox */
kukit.actionsGlobalRegistry.register("lightboxing-cancel", function() {
    var lbparts = ['overlay', 'lightbox', 'lbCloser'];
    for (i=0; i<lbparts.length; i++) {
	document.getElementById(lbparts[i]).style.display = 'none';
    }
    if (LightboxVars.browser == 'Internet Explorer' 
	&& LightboxVars.version != '7') {
	LightboxUtils.setScroll(0, LightboxVars.yPos);
	LightboxUtils.prepareIE("auto", "auto");
	LightboxUtils.hideSelects("visible");
    }

});
kukit.commandsGlobalRegistry.registerFromAction('lightboxing-cancel', 
                                                kukit.cr.makeSelectorCommand);

