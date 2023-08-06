from Products.bibTypes.config import *
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Globals import InitializeClass

Base_Schema = Schema((

    StringField('Abstract',
              searchable=1,
              required=0,
              edit_accessor="editAbstract",
              widget=TextAreaWidget(description="Abstract of the item.",
                                     label="Abstract",
                                     rows=5),
              ),

))

Trailing_Schema = Schema((

    StringField('PublicationUrl',
                required=0,
                searchable=0,
                validators=('isURL',),
                widget=StringWidget(description="The URL to get to the full text of the item.",
                                    label="URL",),
                ),

    StringField('Alt_id',
                required=0,
                searchable=0,
                widget=StringWidget(description="Enter a releveant alternative ID reference, such as PubMed number.",
                                    label="Alternative ID",),
                ),    

    BooleanField('personal_entry',
                 required=0,
                 searchable=0,
                 default=0,
                 widget=BooleanWidget(description="Is the entry a personal resource?",
                                     label="Personal Entry",),
                 ),
    
    ))

base_actions = (
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
    'id' : 'export',
    'name' : 'Export',
    'action' : 'portal_form/export',
    'permissions' : (CMFCorePermissions.View, )
    },
    )

class BibSchema(BaseContent):

    def getAbstract(self):
        # the accessor for dublin core metadata is a bit inconsistent
        # with Archetype
        return self.Description()

    def setAbstract(self, val):
        return self.setDescription(val)

    def editAbstract(self, **kw):
        if hasattr(self,"description"):
            return self.description
        else:
            return ""
    

InitializeClass(BibSchema)    