CubicWeb.require('ajax.js');
CubicWeb.require('htmlhelper.js');

/* callback called when tag-edition is finished */
function validateTags(eid) {
    var input = jQuery('#tagformholder' + eid + ' input')[0];
    var taglist = map(jQuery.trim, input.value.split(','));
    var d = asyncRemoteExec('tag_entity', eid, taglist);
    d.addCallback(function(tagsbarcontent) {
 	reloadComponent('tags_box', rql_for_eid(eid), 'boxes', 'tags_box'+eid);
  	document.location.hash = '#header';
	jQuery('#tagformholder' + eid).empty();
 	updateMessage(_("entity has been tagged"));
    });
}

function removeTag(eid, tageid) {
    var d = asyncRemoteExec('untag_entity', eid, tageid);
    d.addCallback(function(tagsbarcontent) {
 	reloadComponent('tags_box', rql_for_eid(eid), 'boxes', 'tags_box'+eid);
  	document.location.hash = '#header';
 	updateMessage(_("tag has been removed"));
    });
}

function showTagSelector(eid, oklabel, cancellabel) {
    var holder = jQuery('#tagformholder' + eid);
    if (holder.children().length) {
	holder.empty();
    }
    else {
	var deferred = asyncRemoteExec('unrelated_tags', eid);
	deferred.addCallback(function (taglist) {
	    var input = INPUT({'type': 'text', 'id': 'actag_' + eid, 'size': 20});
	    holder.append(input).show();
	    jQuery(input).keypress(function (event) {
		if (event.keyCode == KEYS.KEY_ENTER) {
		    // XXX not very user friendly: we should test that the suggestions
		    //     aren't visible anymore
		    validateTags(eid);
		}
	    });
	    var ok_cancel = DIV({'class' : "sgformbuttons"},
 	                        A({'href' : "javascript: noop();",
	                           'onclick' : 'validateTags(' + eid + ')'},
                                   oklabel),
			        ' / ',
     			        A({'href' : "javascript: noop();",
			           'onclick' : 'jQuery("#tagformholder' + eid + '").empty()'},
                                   cancellabel));
	    holder.append(ok_cancel);
	    jqNode('actag_' + eid).autocomplete(taglist, {
		multiple: true,
		max: 15
	    });
	    jQuery(input).focus();
	});
    }
}

CubicWeb.provide('tag.js');
