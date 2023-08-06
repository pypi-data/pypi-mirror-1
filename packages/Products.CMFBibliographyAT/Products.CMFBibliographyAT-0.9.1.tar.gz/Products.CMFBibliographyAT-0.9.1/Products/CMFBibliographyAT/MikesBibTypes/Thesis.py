from Products.bibTypes.config import *
from Products.bibTypes.base_fields import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema +  Base_Schema + Schema((

    StringField('Level',
                required=1,
                searchable=1,
                widget=StringWidget(description="The level of the thesis, in the format: PhD.",
                                    label="Level",),
                ),

    StringField('Institution',
                required=1,
                searchable=1,
                widget=StringWidget(description="The name of the instituion that granted the degree.",
                                    label="Institution",),
                ),

    IntegerField('PublishYear',
                  required=1,
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

class Thesis(BibSchema):
    """A bibliographic record of a thesis"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 0
    filter_content_types = 1
    archetype_name = "Thesis"

registerType(Thesis)
