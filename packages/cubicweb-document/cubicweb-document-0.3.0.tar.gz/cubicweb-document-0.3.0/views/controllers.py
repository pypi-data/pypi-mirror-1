"""document controllers

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import ValidationError
from cubicweb.web.controller import Controller
from cubicweb.web import Redirect

# translation/revision state ######################################################################

class DocumentSetUpToRevisionController(Controller):
    """simple controller setting the up_to_revision relation for a folder"""
    id = 'documentsetuptorev'

    def publish(self, rset=None):
        """publish the current request, with an option input rql string
        (already processed if necessary)
        """
        for eid in self.req.edited_eids():
            formparams = self.req.extract_entity_params(eid, minparams=2)
            folder = self.req.eid_rset(eid).get_entity(0, 0)
            folder.complete()
            rev = int(formparams['up_to_revision'].split()[0])
            folder.set_up_to_revision(rev)
        goto = self.req.form.get('__redirectpath')
        if goto:
            raise Redirect(self.req.build_url(goto))
        raise Redirect(folder.absolute_url())


