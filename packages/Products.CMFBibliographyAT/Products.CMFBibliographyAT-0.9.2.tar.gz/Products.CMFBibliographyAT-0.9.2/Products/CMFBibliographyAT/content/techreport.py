##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Techreport reference main class"""

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
    import institutionField, typeField, numberField, addressField


SourceSchema = Schema((
    institutionField,
    typeField,
    numberField,
    addressField,
    ))

TechreportSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                   SourceSchema.copy() + TrailingSchema.copy()
TechreportSchema.get('authors').required = 1
TechreportSchema.get('publication_year').required = 1
TechreportSchema.get('institution').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
TechreportSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }


class TechreportReference(BaseEntry):
    """ content type to make reference to a technical report.
    """
    security = ClassSecurityInfo()
    archetype_name = "Techreport Reference"
    source_fields = ('institution', 'publication_type', 'number', 'address',)

    schema = TechreportSchema
    
    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default technical report source format
        """
        try:

            return self.TechreportSource()

        except AttributeError:

            institution 		= self.getInstitution()
            publication_type        	= self.getPublication_type()
            number      		= self.getNumber()
            address     		= self.getAddress()
            
	    source = institution
	    if publication_type: 
		source += ', %s' % publication_type
		if number: source += '(%s)' % number
	    if address: source += ', %s' % address	
	
            return source + '.'


registerType(TechreportReference, PROJECTNAME)
