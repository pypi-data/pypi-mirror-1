"""action links used by the document cube

:organization: Logilab
:copyright: 2008, 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import implements, one_line_rset
from cubicweb.web import action

from cubes.document.views.selectors import (
    lang_is_defined, master_document, translatable)


class DocumentPutTranslation(action.Action):
    id = 'documentputtranslation'
    __select__ = (one_line_rset() & implements('VersionedFile')
                  & lang_is_defined() & master_document() & translatable())

    title = _('upload document translation')
    category = 'mainactions'

    def url(self):
        return self.entity(0, 0).absolute_url(vid='documentuploadnewtranslationform')


class VcsAddAction(action.Action):
    id = 'vcsaddaction'
    __select__ = one_line_rset() & implements('File')

    title = _('add this file in the repository')
    category = 'mainactions'

    def url(self):
        return self.entity(0, 0).absolute_url(vid='vcsaddform')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    # disable some vcsfile actions
    from cubes.vcsfile.views import actions
    for actioncls in (actions.VFHEADRevisionAction,
                      actions.VFAddRevisionAction,
                      actions.VFAllRevisionsAction):
        vreg.unregister(actioncls)
