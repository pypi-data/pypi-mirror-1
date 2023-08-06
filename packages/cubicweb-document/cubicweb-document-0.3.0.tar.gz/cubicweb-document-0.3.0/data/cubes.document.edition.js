
/* XXX we should have something in cw ...
 *     reloadComponent(vid, rql, 'views', divid)  */
function reloadDiv(divid, rql) {
  var thediv = jQuery('#' + divid);
  var url = baseuri() + 'json?rql=' + rql + '&fname=view&vid=' + divid.replace('-', '_');
  thediv.loadxhtml(url);
}

function update_edition_status(vfrql, usereid, will_edit) {
  remoteExec('update_edition_status', vfrql, usereid, will_edit);
  reloadComponent('edit_box', vfrql, 'boxes', 'edit_box');
  reloadDiv('edition-status', vfrql);
  return reloadBox('user_worklist_box');
}
