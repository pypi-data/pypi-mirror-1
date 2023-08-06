from Products.bibTypes.config import *
from Products.bibTypes.base_fields import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema +  Base_Schema + Schema((

    StringField('Series',
                required=0,
                searchable=1,
                widget=StringWidget(description="The title of the series.",
                                    label="Series",),
                ),    

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
                                       label="Publication date"),
                  ),

    StringField('StandardNo',
                required=0,
                searchable=1,
                widget=StringWidget(description="The standard of the report.",
                                    label="Standard Number",),
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

class Standard(BibSchema):
    """A bibliographic record of a standard"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 0
    filter_content_types = 1
    archetype_name = "Standard"

registerType(Standard)
