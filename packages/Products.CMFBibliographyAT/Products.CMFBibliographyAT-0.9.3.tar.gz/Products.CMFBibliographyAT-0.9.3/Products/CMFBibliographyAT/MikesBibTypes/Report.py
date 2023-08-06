from Products.bibTypes.config import *
from Products.bibTypes.base_fields import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema +  Base_Schema + Schema((

    )) + Trailing_Schema

actions = (
    {
    'id' : 'view',
    'name' : 'View',
    'action' : 'base_view',
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
    )

class Report(BaseContent):
    """A bibliographic record of a report"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 0
    filter_content_types = 1
    archetype_name = "Report"

registerType(Report)
