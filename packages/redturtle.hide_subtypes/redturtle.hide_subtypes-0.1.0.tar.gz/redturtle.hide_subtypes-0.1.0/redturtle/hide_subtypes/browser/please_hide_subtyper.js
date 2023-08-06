/**
 * jQuery snippet for hiding the ugly Sub-types menu when not useful
 */

/**
 * Hide the subtyper menu when empty.
 * On page loading this can make a little blink effect.
 */
function hideSubtyperMenu(subtyper_menu) {
	if (jq("dd.actionMenuContent", subtyper_menu).length==0) subtyper_menu.hide();
}

/**
 * Show the subtyper menu when non empty.
 * If CSS style make it invisible at loading, this way will not blink.
 */
function showSubtyperMenu(subtyper_menu) {
	if (jq("dd.actionMenuContent", subtyper_menu).length>0) subtyper_menu.show();
}

function showOrHideSubtyperMenu() {
	var subtyper_menu = jq("#subtypes");
	if (subtyper_menu.length>0)
		subtyper_menu.is(":visible")?hideSubtyperMenu(subtyper_menu):showSubtyperMenu(subtyper_menu);
}

if (window.registerPloneFunction)
	registerPloneFunction(showOrHideSubtyperMenu);
else
	jq(document).ready(showOrHideSubtyperMenu);

