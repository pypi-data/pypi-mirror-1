"""forms used by the document cube

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import implements
from cubicweb.view import EntityView
from cubicweb.common import tags
from cubicweb.web import eid_param
from cubicweb.web.form import FormViewMixIn
from cubicweb.web.formfields import StringField
from cubicweb.web.formwidgets import Select, SubmitButton

from cubes.vcsfile.views import forms
from cubes.document.html import div, ul, li, span

def up_to_revision_form(vdoc):
    req = vdoc.req
    branch = vdoc.head.from_revision[0].branch
    form = vdoc.vreg.select_object('forms', 'base', req, None, entity=vdoc,
                                   form_renderer_id='base',
                                   action=vdoc.req.build_url('documentsetuptorev'),
                                   form_buttons=[SubmitButton()])
    uptorev = vdoc.up_to_revision()
    if uptorev is None:
        uptorev = -1
    vocab = ['%s (%s)' % (rev, branch)
             for rev, _author, _msg, br in vdoc.master_document.revnum_author_msg_branch()
             if br == branch and rev > uptorev]
    uptorev = vdoc.up_to_revision()
    if uptorev is not None:
        vocab = [rev for rev in vocab if rev > uptorev]
    form.append_field(StringField(name="up_to_revision", eidparam=True,
                                  label=_('change to :'), widget=Select,
                                  choices=vocab))
    return form.form_render()


class DocumentUploadNewFormView(forms.VFUploadFormView):
    """upload a new document"""
    id = 'documentuploadnewform'
    __select__ = implements('Folder')

    controller = 'documentuploadnew'

    def form_title(self, _entity):
        return self.req._('Upload a new document')


class DocumentUploadTranslationFormView(forms.VFUploadFormView):
    """upload a new translation of a document"""
    id = 'documentuploadnewtranslationform'
    __select__ = implements('VersionedFile')

    controller = 'documentuploadtranslation'

    def form_title(self, entity):
        return self.req._('Upload a new translation for %s') % tags.a(
            entity.dc_title(), href=entity.absolute_url())

    def additional_form_fields(self, form, entity):
        vocab = [('%s (%s)' % (self.req._(name), code), eid)
                 for eid, code, name in entity.untranslated_langs]
        form.append_field(StringField(name=_('lang'), eidparam=True,
                                      widget=Select, choices=vocab))


class ShowDiffFormView(FormViewMixIn, EntityView):
    """show diff between two revisions"""
    id = 'diffform'
    __select__ = implements('VersionedFile')

    def cell_call(self, row, col, **_kwargs):
        _ = self.req._
        return u'NOT IMPLEMENTED'
        # XXX generic diff for vcsfile
