from Products.bibTypes.config import *
from Products.bibTypes.base_fields import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema +  Base_Schema + Schema((

    StringField('Publisher',
                required=0,
                searchable=1,
                widget=StringWidget(description="The name of the publisher.",
                                    label="Publisher",),
                ),

    IntegerField('PublishYear',
                  required=0,
                  searchable=0,
                  validators=('isInt',),
                  widget=IntegerWidget(description="Enter the year of publication.",
                                       label="Publication Year"),
                  ),

    StringField('ISSN',
                required=0,
                searchable=0,
                widget=StringWidget(description="The ISSN of the journal.",
                                    label="ISSN"),
                ),
    )) + Trailing_Schema

actions = (
    {
    'id' : 'view',
    'name' : 'View',
    'action' : 'base_view',
    'permissions' : (CMFCorePermissions.View, )
    },
    ) + base_actions

class Journal(BibSchema):
    """A bibliographic record of a journal"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 0
    filter_content_types = 1
    archetype_name = "Journal"
    
registerType(Journal)