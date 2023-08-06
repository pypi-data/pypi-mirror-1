"""most views used by the document cube

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement

import uuid
from logilab.mtconverter import html_escape

from cubicweb.web.box import RQLBoxTemplate
from cubicweb.web.htmlwidgets import BoxWidget
from cubes.document.html import div, span, newspace

_ = unicode

class BrowsingWidget(BoxWidget):
    islist = False
    done = False

    def render(self, frombox, rset, treeid):
        w = self.w = frombox.w
        with div(w, Class=self._class, id=self.id):
            with div(w, Class="boxTitle"):
                w(span(html_escape(self.title)))
            with div(w, Class=self.main_div_class):
                frombox.wview('filetree', rset=rset, treeid=treeid)
            with div(w, Class="shadow"):
                w(newspace)

class ReposBrowsingBox(RQLBoxTemplate):
    id = 'browsing_box'
    title = _('browse the repositories')
    visible = True
    # XXX check
    rql = 'Any F,N ORDERBY N WHERE F is Folder, F name N, REPO root_folder RF, F filed_under RF'
    # for the etype_rtype_selector
    etype = 'Folder'
    rtype = 'filed_under'
    order = 2

    def call(self, **kwargs):
        rset = self.req.execute(self.rql)
        if not rset:
            return
        self.req.add_css('jquery.treeview.css')
        self.req.add_js(('cubicweb.ajax.js', 'jquery.treeview.js', 'cubicweb.widgets.js'))
        treeid = self.req.get_session_data('repotree', default=uuid.uuid1().hex)
        self.req.set_session_data('repotree', treeid)
        box = BrowsingWidget(self.req._(self.title), self.id)
        box.render(self, rset=rset, treeid=treeid)
