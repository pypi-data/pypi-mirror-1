"""document components

:organization: Logilab
:copyright: 2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
_ = unicode

from logilab.mtconverter import html_escape

from cubicweb.common.uilib import cut
from cubicweb.selectors import match_context_prop, yes
from cubicweb.web.views.ibreadcrumbs import BreadCrumbComponent
from cubicweb.web.component import Component

from cubes.document.entities import _get_branch_scope
from cubes.docaster.views.widgets import select_widget
from cubes.document.html import form, link


def build_url(elt, maxtextsize):
    try:
        return link(elt.absolute_url(),
                    html_escape(cut(elt.dc_title(), maxtextsize)))
    except AttributeError: # we got an unicode
        return elt

class BreadCrumbs(BreadCrumbComponent):
    visible = True

    def call(self, view=None, first_separator=True):
        entity = self.entity(0)
        path = entity.breadcrumbs(view)
        if path:
            textsize = self.req.property_value('navigation.short-line-size')
            sep = self.separator
            w = self.w
            w(u'<span class="pathbar">%s' % sep)
            for elt in path[:-1]:
                w(build_url(elt, textsize))
                w(sep)
            elt = path[-1]
            w(build_url(elt, textsize))
            self.w(u'</span>')

from cubicweb.web.views.basetemplates import HTMLPageHeader

class OurHTMLHeader(HTMLPageHeader):
    id = 'header'

    def main_header(self, view):
        """build the top menu with authentification info and the rql box"""
        self.w(u'<table id="header"><tr>\n')
        self.w(u'<td id="firstcolumn">')
        self.vreg.select_component('logo', self.req, self.rset).render(w=self.w)
        self.w(u'</td>\n')
        # appliname and breadcrumbs
        self.w(u'<td id="headtext">')
        for compname in ('appliname', 'branch_scope_chooser', 'breadcrumbs'):
            comp = self.vreg.select_component(compname, self.req, self.rset, view=view)
            if comp and comp.propval('visible'):
                comp.render(w=self.w)
        self.w(u'</td>')
        # logged user and help
        self.w(u'<td>\n')
        comp = self.vreg.select_component('loggeduserlink', self.req, self.rset)
        comp.render(w=self.w)
        self.w(u'</td><td>')
        helpcomp = self.vreg.select_component('help', self.req, self.rset)
        if helpcomp: # may not be available if Card is not defined in the schema
            helpcomp.render(w=self.w)
        self.w(u'</td>')
        # lastcolumn
        self.w(u'<td id="lastcolumn">')
        self.w(u'</td>\n')
        self.w(u'</tr></table>\n')
        self.wview('logform', rset=self.rset, id='popupLoginBox', klass='hidden',
                   title=False, message=False)



class BranchScopeComponent(Component):
    """tiny widget to control the branch under which all furthers
    views and actions are scoped"""
    id = 'branch_scope_chooser'
    order = 1
    property_defs = {
        _('visible'):  dict(type='Boolean', default=True,
                            help=_('display the branch chooser or not')),
    }

    def call(self):
        w = self.w
        self.req.add_js( 'cubicweb.ajax.js' )
        repository = self.req.execute('Repository R WHERE R path %(rpath)s',
                                      {'rpath' : self.config.get('main-repository')}).get_entity(0,0)
        curr_branch = _get_branch_scope(self.req)
        choices = repository.branches()
        w(u'<span class="pathbar">&nbsp;')
        select_widget(w, zip(choices, choices), selected=curr_branch,
                      id='branch_scope',
                      onchange=("asyncRemoteExec('set_cookie', 'branch_scope',"
                                "                jQuery('#'+this.id).val());"))
        w(u'</span>')

def registration_callback(vreg):
    vreg.register(BranchScopeComponent)
    vreg.register_and_replace(OurHTMLHeader, HTMLPageHeader)
    vreg.register_and_replace(BreadCrumbs, BreadCrumbComponent)
