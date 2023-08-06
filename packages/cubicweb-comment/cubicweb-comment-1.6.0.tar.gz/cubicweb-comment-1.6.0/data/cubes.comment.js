/*
 *  :organization: Logilab
 *  :copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 *  :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
 */

CubicWeb.require('python.js');
CubicWeb.require('htmlhelpers.js');
CubicWeb.require('ajax.js');

function _getText(textarea) {
    if (typeof(FCKeditor) != 'undefined') {
	var fck = FCKeditorAPI.GetInstance(textarea.id);
	if (fck) {
	    return fck.GetHTML();
	}
    }
    return textarea.value;
}

/* this function is called on inlined-comment editions
 * It calls the add_comment method on the jsoncontroller and reload
 * the comment's component
 */
function processComment(eid, funcname) {
    var buttonbar = jQuery('#comment' + eid + 'bbar').hide();
    var divNode = jQuery('#comment' + eid + 'Slot');
    var textarea = divNode.find('textarea')[0];
    var comment = _getText(textarea);
    if (funcname) {
	// store original value for edit cancel
	textarea.setAttribute('cubicweb:origval', comment);
	var format = 'text/html'; // no select widget if fckeditor is used
	var select = divNode.find('select')[0];
	if (select) {
	    format = firstSelected(select);
	}
	d = asyncRemoteExec(funcname, eid, comment, format);
	d.addCallback(function () {
	    var rooteid = getNode('commentsectionComponent').getAttribute('cubicweb:rooteid');
	    reloadComponent('commentsection', rql_for_eid(rooteid), 'contentnavigation');
	});
    } else { // this is of course terrbily inefficient since we reload the whole tree
	var rooteid = getNode('commentsectionComponent').getAttribute('cubicweb:rooteid');
	reloadComponent('commentsection', rql_for_eid(rooteid), 'contentnavigation');	
    }
}

$(document).ready(function() {
    function scroll_top(event){
        toggleVisibility('popupLoginBox');
        $('html, body').animate({scrollTop:0}, 'fast');
        return false;
    }
    $('a.loadPopupLogin').click(scroll_top);
});

CubicWeb.provide('ecomment.js');

