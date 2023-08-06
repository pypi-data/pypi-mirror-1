/**
 * Manage the opening of external links in a different browser window.
 * 
 * Make this possible for:
 * 1) Link opened by Kupu/TinyMCE, where the (A)nchor behave the "external-link" class
 * 2) Every link with a rel="external" attribute
 * 
 * See also http://www.regione.emilia-romagna.it/wcm/LineeGuida/sezioni/tecnici/script.htm
 */

var NEW_WINDOW_TITLE_LABEL = 'il collegamento apre una nuova finestra'; 

/**
 * To be loaded when page is load.
 * Look for anchors and make right ones open in new window.
 */
function externalLinks() {
	var anchors = jq("a[rel=external], a.external-link");
	makeAllExternalLink(anchors);
}

/**
 * Make all passed anchors to be opened in new window.
 * @param {jQuery} anchors sequence of anchors to act on
 */
function makeAllExternalLink(anchors) {
	anchors.attr('title', function (indexArray) {
		if (this.title) return this.title + ' - '+ NEW_WINDOW_TITLE_LABEL;
		else return NEW_WINDOW_TITLE_LABEL;
	});
	anchors.click(function( ) { window.open( this.href ); return false; });
	anchors.keypress(function(e) { k = (e) ? e.keyCode : window.event.keyCode; if (k==13) window.open(this.href); return false; });
}

registerPloneFunction(externalLinks);
