"""this contains the server-side hooks triggered at entities/relation
creation/modification times

:organization: Logilab
:copyright: 2008,2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import sep, basename

from cubicweb.server.hooksmanager import Hook

from cubes.document.entities.folder import lookup_folder_by_path

class AddRepository(Hook):
    events = ('after_add_entity',)
    accepts = ('Repository',)

    def call(self, session, entity):
        # make a root folder matching this repo and the subpath
        # important assumption : this is a root folder
        reponame = basename(entity.path)
        repofolder = session.execute('Folder F WHERE F name %(name)s',
                                     {'name' : reponame})
        if not repofolder:
            repofolder = session.execute('INSERT Folder F: F name %(name)s',
                                         {'name' : reponame})
        session.execute('SET R root_folder F WHERE R eid %(reid)s, F eid %(feid)s',
                        {'reid' : entity.eid, 'feid' : repofolder.rows[0][0]})
        assert repofolder, 'impossible to create a Folder for the repo'
        if entity.subpath:
            subpath = entity.subpath.split(sep)
            lastfolder = lookup_folder_by_path(session.execute, repofolder.rows[0][0],
                                               subpath, create_missing=True)
            assert lastfolder

# disable the vcsfile.AddVersionedFile hook
from cubes.vcsfile.hooks import AddVersionedFileHook as VCSAddVersionedFileHook
VCSAddVersionedFileHook.enabled = False

class AfterAddVersionedFile(Hook):
    """
    * set VersionedFile filed_under the right Folder automatically
      according to their path in the repository
    * may create a Folder hierarchy matching the correct path if it
      is not already there
    """
    events = ('after_add_entity', )
    accepts = ('VersionedFile',)

    def call(self, session, vfile):
        if hasattr(vfile, '_cw_recreating'):
            return
        # folder hierarchy lookup/construction
        dirs = vfile.directory.split(sep)
        try:
            repoeid = vfile.querier_pending_relations[('from_repository', 'subject')]
            repo = session.eid_rset(repoeid).get_entity(0, 0)
        # catch AttributeError since vfile has no querier_pending_relations
        # when it has been discovered by the vcs source
        except (AttributeError, KeyError):
            repo = vfile.from_repository[0]
        root = repo.root_folder[0]
        rooteid = root.eid
        foldereid = lookup_folder_by_path(session.execute,
                                          rooteid,
                                          vfile.directory.split(sep),
                                          create_missing=True)
        session.execute('SET X filed_under F WHERE X eid %(x)s, F eid %(f)s',
                        {'x': vfile.eid, 'f': foldereid}, 'x')
