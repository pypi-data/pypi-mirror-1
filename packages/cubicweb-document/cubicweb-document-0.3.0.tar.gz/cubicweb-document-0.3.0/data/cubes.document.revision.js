// This contains revisions-specific javascript

function check_boxes_of(elt, entity_eid) {
    /* highly coupled to versioned file revisions view (views/secondary)  */
    var checked = [];
    var unchecked = [];
    $(elt).find("input").each(function(){
        if (this.checked) {
            if (checked.length > 2) {
                this.checked = false;
                unchecked.push(this);
            }
            else checked.push(this); }
        else unchecked.push(this);
    });
    if (checked.length > 1) {
        $("#documentdiff").show();
        var rev1 = 'rev1:' + entity_eid;
        var rev2 = 'rev2:' + entity_eid;
        jqNode(rev1).attr('value', checked[0].value);
        jqNode(rev2).attr('value', checked[1].value);
        set_input_display_style(elt, 'none');
    }
    if (checked.length < 2) {
        $("#documentdiff").hide();
        set_input_display_style(elt, 'block');
    }
}

function set_input_display_style(elt, style) {
    $(elt).find("input").each(function(){
      if (!this.checked) { this.style.display = style; }});
}

function show_oo_tip_byneed(someid) {
  var node = jqNode(someid);
  node.find('option').each(function() {
    if (this.selected) {
      if (this.value == 'oo')
        $('#diff_tips').show();
      else
        $('#diff_tips').hide();
    }
  });
}

function dispatch_diff(formid) {
  var form = jQuery(formid);
  var choice = form.find('option[selected]')[0].value;
  if (choice == 'oo')
    form.submit();
  else
    {
      var diff_div = jQuery('#inline_diff_content')[0];
      var feid = diff_div.getAttribute('name');
      var rev1 = form.find('input[name=rev1]')[0].value;
      var rev2 = form.find('input[name=rev2]')[0].value;
      var later = asyncRemoteExec('diffview', feid, rev1, rev2);
      later.addCallback(function(req) {
        diff_div.appendChild(getDomFromResponse(req));
        diff_div.style.display = 'block';
      });
      later.addErrback(function(err) {
        log(err);
      });
    }
}
