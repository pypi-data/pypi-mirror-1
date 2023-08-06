from Products.bibTypes.config import *
from Products.bibTypes.base_fields import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema +  Base_Schema + Schema((

#author should be editor

    StringField('Conference',
                required=0,
                searchable=1,
                widget=StringWidget(description="The name of the conference.",
                                    label="Conference",),
                ),    

    StringField('Location',
                required=0,
                searchable=1,
                widget=StringWidget(description="The location of the conference.",
                                    label="Location",),
                ),

    IntegerField('PublishYear',
                  required=0,
                  searchable=0,
                  validators=('isInt',),
                  widget=IntegerWidget(description="Enter the year of publication.",
                                       label="Publication date"),
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

class ConferencePaper(BibSchema):
    """A bibliographic record of a conference paper"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 0
    filter_content_types = 1
    archetype_name = "Conference Paper"

registerType(ConferencePaper)