"""document specific class for Document entities

:organization: Logilab
:copyright: 2008,2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import fetch_config
from cubicweb.interfaces import ITree

from cubes.vcsfile.entities import VersionedFile, VersionContent

from cubes.document.entities import TreeMixin, _get_branch_scope

class VersionedDocument(TreeMixin, VersionedFile):
    __implements__ = VersionedFile.__implements__ + (ITree,)
    fetch_attrs, fetch_order = fetch_config(['name', 'lang', 'pivot_lang'])

    @property
    def abspath(self):
        """omit the root folder, which is fake and whose purpose
        is to group (by filed_under) relation
        """
        return '%s/%s' % (self.filed_under[0].abspath, self.name)

    # edition helpers
    def vcs_rm(self, *args, **kwargs):
        super(VersionedDocument, self).vcs_rm(*args, **kwargs)
        self.reset_edition_status()

    def vcs_upload_revision(self, *args, **kwargs):
        super(VersionedDocument, self).vcs_upload_revision(*args, **kwargs)
        self.reset_edition_status()

    def mark_downloaded_for_edition_by(self, usereid):
        rql = self.req.execute
        rset = rql('Any E WHERE E might_edit VF, VF eid %(selfeid)s, '
                   'E user U, U eid %(ueid)s',
                   {'selfeid' : self.eid, 'ueid' : usereid})
        if not rset:
            rql('INSERT Editor E: E user U, E might_edit VF '
                'WHERE VF eid %(selfeid)s, U eid %(usereid)s',
                {'selfeid' : self.eid, 'usereid' : usereid})

    def unmark_user_for_edition(self, ueid):
        rql = self.req.execute
        rql('DELETE Editor E WHERE E user U, U eid %(usereid)s, '
            'E might_edit VF, VF eid %(selfeid)s',
            {'usereid' : ueid, 'selfeid' : self.eid})

    def reset_edition_status(self):
        "on upload of a new revision, this probably needs to be cleaned up"
        self.req.execute('DELETE Editor E WHERE E might_edit VF, VF eid %(eid)s',
                         {'eid' : self.eid})

    #/edition

    # versioning
    def branch_head(self, branch=None):
        """branch_head that should always have a branch (scoped)"""
        branch = _get_branch_scope(self.req)
        return super(VersionedDocument, self).branch_head(branch)

    def deleted_in_branch(self, branch=None):
        """deleted_in_branch should always have a branch """
        branch = _get_branch_scope(self.req)
        return super(VersionedDocument, self).deleted_in_branch(branch)

    def exists_under_branch_scope(self):
        """does not exists in the branch scope"""
        head = self.branch_head()
        return head is not None

    def up_to_revision(self):
        """return the revision number of the master document where this one has
        been last updated.
        """
        assert not self.pivot_lang
        rql = ('DISTINCT Any MAX(RNUM) WHERE MVC from_revision REV, REV revision RNUM, '
               'VC up_to_revision MVC, VC content_for VF, '
               'VF eid %(selfeid)s')
        rset = self.req.execute(rql, {'selfeid' : self.eid})
        try:
            return rset[0][0]
        except IndexError:
            return None

    def set_up_to_revision(self, uptorev, vcentity=None):
        """mark a revision of this document as up to the given revision of the
        master document.

        If given `vcentity` should be the VersionContent entity which will hold
        the up_to_revision relation, else the latest revision will be used.
        """
        if vcentity is None:
            rql = 'Any MAX(X) WHERE X content_for VF, VF eid %(vfeid)s'
            rset = self.req.execute(rql, {'vfeid': self.eid})
            vcentity = rset.get_entity(0, 0)
        master = self.master_document
        self.req.execute(
            'SET VC1 up_to_revision VC2 '
            'WHERE VC1 eid %(svc)s, VC2 content_for VF2, '
            'VC2 from_revision REV, REV revision %(rev)s, VC1 is VersionContent, '
            'VC2 is VersionContent, VF2 eid %(meid)s',
            {'svc': vcentity.eid, 'rev': uptorev, 'meid' : master.eid})

    #/versioning

    # i18n
    def dc_language(self):
        lang = self.language
        if lang is None:
            return self.req._('undefined')
        return self.req._(lang.name)

    @property
    def untranslated_langs(self):
        rql = self.req.execute
        used_langs = [trans.lang[0].eid for trans in self.translations]
        if self.lang:
            used_langs.append(self.lang[0].eid)
        if used_langs:
            return rql('Any L,C,N WHERE NOT L eid in (%s), L is Language, '
                       'L code C, L name N' % ','.join(str(eid) for eid in used_langs))
        else:
            return rql('Any L,C,N WHERE L is Language, L code C, L name N')
