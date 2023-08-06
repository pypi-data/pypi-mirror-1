from Products.bibTypes.config import *
from Products.bibTypes.base_fields import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema +  Base_Schema + Schema((

    StringField('BookTitle',
                required=0,
                searchable=1,
                widget=StringWidget(description="The title of the book.",
                                    label="Book Title",),
                ),    

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

    StringField('Edition',
                required=0,
                searchable=1,
                widget=StringWidget(description="The edition of the book.",
                                    label="Edition",),
                ),

    IntegerField('PublishYear',
                  required=0,
                  searchable=0,
                  validators=('isInt',),
                  widget=IntegerWidget(description="Select the year of publication.",
                                       label="Publication date"),
                  ),

    StringField('ISBN',
                required=0,
                searchable=0,
                widget=StringWidget(description="The ISBN of the book.",
                                    label="ISBN",),
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

class Chapter(BibSchema):
    """A bibliographic record of a chapter in a book"""
    schema = schema
    actions = actions
    include_default_actions = 0
    global_allow = 0
    filter_content_types = 1
    archetype_name = "Chapter"

registerType(Chapter)
