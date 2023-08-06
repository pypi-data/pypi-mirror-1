# document schema

CWUser = import_erschema('CWUser')
Repository = import_erschema('Repository')
VersionedFile = import_erschema('VersionedFile')

VersionedFile.add_relation(SubjectRelation('Folder'), name='filed_under')
VersionedFile.permissions = {
    'read':   ('managers', 'users'),
    'add':    ('managers', 'users',),
    'update': ('managers', 'users', 'owners'),
    'delete': ()}

Repository.add_relation(SubjectRelation('Folder', cardinality='??'), name='root_folder')

# Edition conflict tool
class Editor(EntityType):
    permissions = {'read': ('managers', 'users'),
                   'add': ('managers', 'users'),
                   'update': ('managers', 'owners'),
                   'delete': ('managers', 'owners')}
    user = SubjectRelation('CWUser', description=_('user'), cardinality='1*')
    might_edit = SubjectRelation('VersionedFile', description=_('odt likely downloaded for edition'))


# I18n
i18npermissions = {'read' :   ('managers', 'users'),
                   'add' :    ('managers', 'users'),
                   'delete' : ('managers', 'users') }
lang_def = import_erschema('lang')
lang_def.permissions = i18npermissions.copy()

# XXX (syt) what's the point of this function?
# marking a bunch of vars as strictly of local interest
def set_pivot_lang_perms(perms):
    pivot_lang_def = import_erschema('pivot_lang')
    perms = perms.copy()
    perms['update'] = ('managers', 'users')
    pivot_lang_def.permissions = perms
set_pivot_lang_perms(i18npermissions)

import_erschema('translation_of').permissions = i18npermissions

class lang(RelationDefinition):
    subject = ('VersionedFile',)
    object = 'Language'

class translation_of_vf(RelationDefinition):
    name = 'translation_of'
    subject = 'VersionedFile'
    object = 'VersionedFile'

class pivot_lang(RelationDefinition):
    subject = 'VersionedFile'
    object = 'Boolean'

class up_to_revision(RelationType):
    """revision X of translation is up to revision Y of its master document"""
    cardinality = '?*'
    subject = ('VersionContent', 'DeletedVersionContent')
    object = ('VersionContent', 'DeletedVersionContent')
    constraints = [RQLConstraint('O content_for OVF, S content_for SVF, '
                                 'SVF translation_of OVF')]
