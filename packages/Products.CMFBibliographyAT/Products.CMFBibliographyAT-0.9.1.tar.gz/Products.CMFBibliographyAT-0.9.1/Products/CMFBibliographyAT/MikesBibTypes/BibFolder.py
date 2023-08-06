from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema

actions = (
    {
    'id' : 'view',
    'name' : 'View',
    'action' : 'folder_listing',
    'permissions' : (CMFCorePermissions.View, )
    },
    {
    'id' : 'edit',
    'name' : 'Edit',
    'action' : 'portal_form/base_edit',
    'permissions' : (CMFCorePermissions.ModifyPortalContent, )
    },
    {
    'id' : 'properties',
    'name' : 'Properties',
    'action' : 'portal_form/base_metadata',
    'permissions' : (CMFCorePermissions.ModifyPortalContent, )
    },
    {
    'id' : 'import',
    'name' : 'Import',
    'action' : 'portal_form/import',
    'permissions' : (CMFCorePermissions.ModifyPortalContent, )
    },
    )

class BibFolder(BaseFolder):
    """A folder to contain bibliographic objects"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 1
    filter_content_types = 1
    allowed_content_types = (['Book', 'Journal', 'Article', 'Chapter', 'Thesis', 'Proceedings', 'TechnicalReport', 'ConferencePaper', 'NewsArticle', 'Standard'])
    archetype_name = "Bibliographical Folder"

registerType(BibFolder)