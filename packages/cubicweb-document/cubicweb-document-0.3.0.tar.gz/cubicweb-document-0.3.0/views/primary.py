"""primary views for entities used by the document cube

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
__docformat__ = "restructuredtext en"
_ = unicode

from contextlib import contextmanager

from cubicweb import NoSelectableObject
from cubicweb.selectors import implements
from cubicweb.web.httpcache import GMTOFFSET
from cubicweb.web import uicfg
from cubicweb.web.views.tabs import TabsMixin
from cubicweb.web.views.primary import PrimaryView

from cubes.document.entities import _get_branch_scope
from cubes.document.html import div, span, row_ctx, col_ctx, table
from cubes.document.views.selectors import not_in_branch_scope

#uicfg.autoform_section.tag_subject_of(('Folder', 'filed_under', '*'), False)
for relname in ('translation_of', 'filed_under', 'name', 'directory',
                'from_repository', 'content_for', 'might_edit'):
    uicfg.autoform_section.tag_subject_of(('VersionedFile', relname, '*'), 'generated')

uicfg.autoform_section.tag_subject_of(('VersionedFile', 'lang', '*'), 'secondary')
uicfg.autoform_section.tag_subject_of(('VersionedFile', 'filed_under', '*'), 'generated')

uicfg.actionbox_appearsin_addmenu.tag_object_of(('VersionContent', 'content_for', 'VersionedFile'), False)

@contextmanager
def related_box(w, label):
    with div(w, Class="docRelated"):
        with div(w, Class="sideBoxTitle"):
            w(span(label))
        with div(w, Class="sideBox sideBoxBody"):
            yield


class TabbedDocumentPrimaryView(TabsMixin, PrimaryView):
    __select__ = PrimaryView.__select__ & implements('VersionedFile')
    id = 'primary'
    tabs = [_('document'), _('revisions')]
    default_tab = 'document'

    def render_entity(self, entity):
        """return html to display the given entity"""
        self.req.add_css('cubicweb.form.css')
        self.req.add_js(('cubicweb.tabs.js', 'cubicweb.tabs.js', 'jquery.tablesorter.js',
                         'cubes.document.revision.js', 'cubes.document.edition.js',
                         'cubicweb.edition.js', 'cubicweb.calendar.js'))
        if not entity.exists_under_branch_scope():
            self.wview('document', entity.as_rset())
        elif entity.deleted_in_branch():
            self.wview('primary', entity.branch_head().as_rset())
        else:
            self.render_entity_title(entity)
            self.render_tabs(self.tabs, self.default_tab, entity)

class EntityViewMixin(object):

    def render_entity(self, entity):
        w = self.w
        with table(w, u'', border="0", width="100%"):
            with row_ctx(w):
                with col_ctx(w, style="width:75%", valign="top"):
                    self.render_entity_attributes(entity)
                    self.render_entity_relations(entity)
                with col_ctx(w, valign="top"):
                    self.render_side_related(entity)

class DocumentPrimaryView(EntityViewMixin, PrimaryView):
    __select__ = PrimaryView.__select__ & implements('VersionedFile')
    id = 'document'

    def render_entity_attributes(self, entity):
        entity.branch_head().view('primary', w=self.w)

    def render_side_related(self, entity):
        w = self.w
        for vid in ('master_translation_status', 'non_master_translation_status',
                    'download', 'edition_status'):
            try:
                view = self.vreg.select_view(vid, self.req, self.rset)
            except NoSelectableObject:
                continue
            with related_box(w, self.req._(vid)):
                view.render(w=w)

class DocumentInAnotherBranchPrimary(DocumentPrimaryView):
    __select__ = DocumentPrimaryView.__select__ & not_in_branch_scope()

    def render_entity_attributes(self, entity):
        branch = _get_branch_scope(self.req)
        self.w(_('This document does not exist in the branch named "%s".' % branch))

    def render_entity_relations(self, entity):
        pass

    def render_entity_related(self, entity):
        pass


class FolderPrimaryView(PrimaryView):
    __select__ = PrimaryView.__select__ & implements('Folder')
    id = 'primary'

    def last_modified(self):
        """return the date/time where this view should be considered as
        modified. Take care of possible related objects modifications.
        """
        entity = self.complete_entity(0)
        try:
            return max([entity.modification_date] +
                       [r.modification_date for r in entity.reverse_filed_under]) + GMTOFFSET
        except TypeError:
            # sqlite bug: UNION queries return date as string :(
            return entity.modification_date
