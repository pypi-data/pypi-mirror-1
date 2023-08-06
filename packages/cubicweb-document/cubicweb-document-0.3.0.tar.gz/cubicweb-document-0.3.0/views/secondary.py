"""most views used by the document cube

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
_ = unicode

from logilab.mtconverter import html_escape

from cubicweb.interfaces import ITree
from cubicweb.selectors import implements, one_line_rset
from cubicweb.common.uilib import cut as text_cut, rql_for_eid
from cubicweb.web.views.baseviews import SecondaryView, EntityView, OneLineView

from cubes.document.entities import _get_branch_scope
from cubes.document.views.selectors import lang_is_defined, master_document, is_translation
from cubes.document.views.forms import up_to_revision_form
from cubes.document.html import link, span, div, table, td, row_ctx, p, input, form


class LangView(SecondaryView):
    __select__ = SecondaryView.__select__ & lang_is_defined()
    id = 'lang'

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(link(html_escape(entity.absolute_url()),
                    html_escape(entity.dc_language())))

class InContextView(EntityView):
    """for VersionedFiles, it is nicer to show
    a longer portion of the description
    """
    __select__ = implements('VersionedFile')
    id = 'incontext'

    def cell_call(self, row, col, **_kwargs):
        w = self.w
        entity = self.entity(row, col)
        desc = text_cut(entity.dc_description(), 300)
        w(link(html_escape(entity.absolute_url()),
               html_escape(self.view('textincontext', self.rset, row=row, col=col)),
               title=html_escape(desc)))

class FileItemInnerView(OneLineView):
    """inner view used by the TreeItemView instead of oneline view

    This view adds an enclosing <span> with some specific CSS classes
    around the oneline view. This is needed by the jquery treeview plugin.
    """
    __select__ = OneLineView.__select__ & implements('Folder', 'VersionedFile', 'File')
    id = 'filetree-oneline'

    def cell_call(self, row, col):
        w = self.w; _ = self.req._
        entity = self.entity(row, col)
        if ITree.is_implemented_by(entity.__class__) and not entity.is_leaf():
            w(span(entity.view('oneline'), Class='folder'))
        else:
            branch = _get_branch_scope(self.req)
            if hasattr(entity, 'keyword'):
                name = entity.keyword
            else:
                name = entity.name
            # exists ? deleted ?
            if (hasattr(entity, 'exists_under_branch_scope') and
                not entity.exists_under_branch_scope()):
                name = '%s (not there)' % name
                w(span(html_escape(name), Class='file'))
            elif (hasattr(entity, 'deleted_in_branch') and
                  entity.deleted_in_branch(branch)):
                name = '%s (deleted)' % name
                w(span(html_escape(name), Class='file'))
            else:
                w(span(link(html_escape(entity.absolute_url()),
                            html_escape(name or u'')),
                       Class='file'))

class MasterOdtTranslationStatus(EntityView):
    id = _('master_translation_status')
    __select__ = implements('VersionedFile') & master_document()

    def cell_call(self, row, col):
        _, w = self.req._, self.w
        entity = self.entity(row, col)
        self.field(_('language :'), html_escape(entity.dc_language()), tr=False)
        w(_('this is the master document'))
        if not entity.translations:
            return w(p(_('no translation available yet')))
        ent_rev = entity.branch_head().revision
        with table(w, (_('translation'), _('status')), Class='listing'):
            for translation in entity.translations:
                tr_uptorev = translation.up_to_revision()
                if ent_rev == tr_uptorev:
                    msg = _('up to date')
                    style = 'uptodate'
                elif tr_uptorev is None:
                    msg = _('unknown')
                    style = 'needs_update'
                else:
                    msg = _('up to rev. %s') % tr_uptorev
                    style = 'needs_update'
                with row_ctx(w):
                    w(td(link(html_escape(translation.absolute_url()),
                               translation.dc_language())))
                    w(td(span(msg, Class=style)))

class NonMasterOdtTranslationStatus(EntityView):
    __select__ = implements('VersionedFile') & is_translation()
    id = _('non_master_translation_status')

    def cell_call(self, row, col):
        _, w = self.req._, self.w
        entity = self.entity(row, col)
        self.field(_('language :'), html_escape(entity.dc_language()), tr=False)
        master = entity.master_document
        if not master:
            w(span(_('this document is not a master document and has no master set'),
                   Class="needs_update"))
            return
        self.field(_('master document :'), master.view('lang'), tr=False)
        mheadrev = master.branch_head().revision
        uptorev = entity.up_to_revision()
        status_label = u'<span class="%s">%s</span>'
        if uptorev is not None and uptorev != mheadrev:
            self.field(_('up to revision :'), status_label % ('needs_update', uptorev), tr=False)
            w(up_to_revision_form(entity))
        elif uptorev is None:
            self.field(_('up to revision :'), status_label % ('needs_update', _('unknown')), tr=False)
            w(up_to_revision_form(entity))
        else:
            self.field(_('status :'), status_label % ('uptodate', _('up to date')), tr=False)


class EditionStatus(EntityView):
    __select__ = one_line_rset() & implements('VersionedFile')
    id = _('edition_status')
    _msg_help = _('Users having downloaded the editable version of the document are listed there. '
                  'You might want to coordinate with them to avoid edition conflicts later. '
                  'It is possible to assess one\'s intention not to make modifications.')
    _msg_nouser = _('No single user ever got this document in odt form. '
                    'Or they pretend not to make editions on it.')
    _msg_mightedit = (_('Might edit'), _('Edition conflicts are a pain. '
                                         'You should try to avoid them.'))
    _msg_hewontedit = (_('He will not edit'), _('God forbids !'))
    _msg_iwontedit = _('I will not edit'), _('I swear !')

    def cell_call(self, row, col):
        w, _ = self.w, self.req._
        entity = self.entity(row, col)
        rset = self.req.execute('Any U WHERE E user U, E might_edit VF, VF eid %(vfeid)s ',
                                {'vfeid' : entity.eid})
        self.req.add_js('cubes.docaster.edition.js')
        with div(w, id='edition-status'):
            w(p(_(self._msg_help),
                Class='needsvalidation'))
            if not rset:
                w(p(_(self._msg_nouser),
                    Class='uptodate'))
                return
            with table(w, (_('user'), _('expectations')), Class='listing'):
                for idx, row in enumerate(rset.rows):
                    user = rset.get_entity(idx, 0)
                    this_user = self.req.user
                    if this_user.login == user.login:
                        value, title = self._msg_iwontedit
                    else:
                        if this_user.is_in_group('managers'):
                            value, title = self._msg_hewontedit
                        else:
                            value, title = self._msg_mightedit
                    value, title = _(value), _(title)
                    if user.eid == this_user.eid:
                        status = input(type='button', value=value, title=title, Class='validateButton',
                                       onclick="update_edition_status('%s', %s, false)" % (rql_for_eid(entity.eid),
                                                                                           user.eid))
                    else:
                        status = p(value, title=title)
                    mail = user.use_email[0].address if user.use_email else None
                    userdescr = '%s %s' % (user.firstname or user.login, user.surname or '')
                    userlink = link(html_escape('mailto:%s' % mail), userdescr) if mail else userdescr
                    with row_ctx(w):
                        w(td(userlink))
                        w(td(status))

he = html_escape
class DocumentRevisionsView(EntityView):
    __select__ = implements('VersionedFile')
    id = 'revisions'

    def cell_call(self, row, col):
        _, w = self.req._, self.w
        entity = self.entity(row, col)
        self.req.add_js(('cubes.document.revision.js', 'cubes.document.edition.js'))
        revisions = entity.revnum_author_msg_branch()
        w(p(_('Inline diffs : you can click on the title to make it disappear.'),
            Class='needsvalidation'))
        with form(w, id="revisions_select", method="post", enctype="multipart/form-data",
                  action=entity.build_url('documentdiff')):
            legend = _('check two boxes to see a diff between the corresponding revisions')
            with table(w, headers=(_('show diff'), _('vcs revision'), _('branch'),
                                   _('author'), _('comment'), _('download')),
                       Class='listing', title=legend):
                for rnum, rauthor, rmsg, branch in reversed(revisions):
                    if entity.revision_deleted(rnum):
                        url = ''
                    else:
                        might_edit = str(rnum == entity.branch_head().revision).lower()
                        url = link("javascript:download_document('%s', %s, %s, %s)" % \
                                       (rql_for_eid(entity.eid), self.req.user.eid,
                                        rnum, might_edit),
                                   _('download'))
                    with row_ctx(w):
                        w(td(input(type="checkbox", value="%s" % rnum,
                                   onclick="check_boxes_of('#revisions_select', %s);" % entity.eid)))
                        for elt in (td(rnum), td(branch), td(he(rauthor)),
                                    td(he(rmsg)), td(url)):
                            w(elt)
        with div(self.w, id="documentdiff", style="display: none"):
            self.wview('diffform', self.rset)

class DocumentDiffView(EntityView):
    __select__ = implements('VersionedFile')
    id = 'diff'

    def cell_call(self, row, col, rev1=None, rev2=None, **_kwargs):
        if not (rev1 and rev2):
            return
        entity = self.entity(row, col)
        r1 = int(rev1)
        r2 = int(rev2)
        assert r1 != r2, '%s == %s' % (r1, r2)
        if r1 > r2:
            r1, r2 = r2, r1
        rev1 = entity.revision(r1).data
        rev2 = entity.revision(r2).data
        with div(self.w, onclick="jqNode(this).hide('fast')"):
            self.w(h(1, self.req._('Content diff (revision %s to %s)') % (r1, r2)))
            from difflib import ndiff
            self.w(ndiff(rev1, rev2))
