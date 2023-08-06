/*
 *  :organization: Logilab
 *  :copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 *  :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
 */

function displayImg(eid) {
    var deferred = asyncRemoteExec('get_image', eid);
    deferred.addCallback(function (response){
	var html = getDomFromResponse(response);
	jQuery('img.selectedimg').removeClass('selectedimg');
	jQuery('#img'+eid).addClass('selectedimg');
	jQuery('#imageholder').empty().append(html);
    });
}
