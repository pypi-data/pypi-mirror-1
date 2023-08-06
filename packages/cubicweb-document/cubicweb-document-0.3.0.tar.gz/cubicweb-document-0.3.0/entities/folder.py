"""document specific class for Folder entities

:organization: Logilab
:copyright: 2008,2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import fetch_config

from cubes.folder.entities import Folder as BaseFolder
from cubes.document.entities import _get_branch_scope

class Folder(BaseFolder):
    fetch_attrs, fetch_order = fetch_config(['name'])

    @property
    def repository(self):
        return self.root().reverse_root_folder[0]

    @property
    def abspath(self):
        """omit the root folder, which is fake and whose purpose
        is to group (by filed_under) relation
        """
        parentfolders = list(self.iterparents())
        parentfolders.insert(0, self)
        parentfolders.pop()
        return u'/'.join(foldr.name for foldr in reversed(parentfolders))

    def is_leaf(self):
        return False

    def breadcrumbs(self, view, recurs=False):
        if self.reverse_root_folder:
            return []
        parent = self.parent()
        if parent:
            return parent.breadcrumbs(view, True) + [self]
        return []

    def vcs_rm(self, rev=None, **kwargs):
        """
        recursively link DeletedVersionContent to its versioned_(sub)folders
        and versioned files"""
        if rev is None:
            msg = kwargs.get('msg') or self.req._('deleted %s') % self.dc_title()
            rev = self.repository.make_revision(msg=msg, branch=_get_branch_scope(self.req))
        def recursively_mark_deleted(folder):
            for vfile in folder.leaves():
                vfile.vcs_rm(rev)
            for subfolder in folder.children():
                recursively_mark_deleted(subfolder)
        recursively_mark_deleted(self)



def lookup_folder_by_path(executor, rootfoldereid, pathlist, create_missing=False):
    """
    looks up a folder matching a pathname list
    starting from a (root) folder eid
    optionally create a whole (sub)path, a la makedirs
    """
    if not pathlist:
        return

    class FolderFound(Exception): pass
    class FolderNotFound(Exception): pass

    def _lookup_folder(folderseid, pathlist):
        if not pathlist:
            raise FolderFound(folderseid[-1])
        parent = folderseid[-1]
        curpath = pathlist.pop()
        folder = executor('Folder X WHERE X name %(name)s, X filed_under PF, PF eid %(pfeid)s',
                          {'name': curpath, 'pfeid': parent})
        if not folder:
            if not create_missing:
                raise FolderNotFound('/'.join(list(reversed(pathlist))))
            folder = executor('INSERT Folder F: F name %(name)s', {'name' : curpath})
            foldereid = folder.rows[0][0]
            executor('SET F filed_under PF WHERE F eid %(feid)s, PF eid %(pfeid)s',
                     {'feid' : foldereid, 'pfeid' : parent})
        else:
            foldereid = folder.rows[0][0]
        folderseid.append(foldereid)
        _lookup_folder(folderseid, pathlist)

    try:
        _lookup_folder([rootfoldereid], filter(None, reversed(pathlist)))
    except FolderNotFound:
        return
    except FolderFound, ff:
        return ff.args[0]
