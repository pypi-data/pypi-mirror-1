##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Phdthesis reference main class"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField, StringWidget
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import registerType

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import schoolField, addressField, typeField


SourceSchema = Schema((
    typeField,
    schoolField,
    addressField,
     ))

PhdthesisSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                  SourceSchema.copy() + TrailingSchema.copy()
PhdthesisSchema.get('authors').required = 1
PhdthesisSchema.get('school').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
PhdthesisSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class PhdthesisReference(BaseEntry):
    """ content type to make reference to a PhD thesis.
    """
    security = ClassSecurityInfo()
    archetype_name = "Phdthesis Reference"
    source_fields = ('school', 'address', 'publication_type',)

    schema = PhdthesisSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default source renderer
        """
        try:
            return self.PhdthesisSource()
        except AttributeError:
            publication_type  	= self.getPublication_type()
            school  		= self.getSchool()
            address 		= self.getAddress()
            
            if publication_type:
                source = publication_type
            else:
                source = 'PhD thesis'
	    if school: source += ', %s' % school
	    if address: source += ', %s' % address
	
	    return source + '.'

registerType(PhdthesisReference, PROJECTNAME)
