##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Proceedings reference class"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField, BooleanField
    from Products.LinguaPlone.public import StringWidget, BooleanWidget
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField, BooleanField
    from Products.Archetypes.public import StringWidget, BooleanWidget
from Products.Archetypes.public import registerType

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import publisherField, addressField, volumeField, numberField, \
           organizationField, seriesField, editor_flagField
from Products.CMFBibliographyAT.content.book \
    import AuthorTrailingSchema

ThisAuthorTrailingSchema = AuthorTrailingSchema.copy()
ThisAuthorTrailingSchema['editor_flag'].default=1
ThisAuthorTrailingSchema['editor_flag'].widget.description='Leave this checked unless the people specified above are not the editors of this proceedings volume.'
ThisAuthorTrailingSchema['editor_flag'].widget.description_msgid='help_editor_flag_checked'
ThisAuthorTrailingSchema['editor_flag'].mode='r'

SourceSchema = Schema((
    publisherField,
    addressField,
    volumeField,
    numberField,
    organizationField,
    seriesField,
    ))

ProceedingsSchema = HeaderSchema.copy() + AuthorSchema.copy() + ThisAuthorTrailingSchema.copy() + \
                    CoreSchema.copy() + SourceSchema.copy() + TrailingSchema.copy()
ProceedingsSchema.get('authors').required = 0
ProceedingsSchema.get('publication_year').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
ProceedingsSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class ProceedingsReference(BaseEntry):
    """ content type to make reference to a book.
    """
    security = ClassSecurityInfo()
    archetype_name = "Proceedings Reference"
    source_fields = ('publisher', 'address', 'volume', 'number', 'organization', 'series',)

    schema = ProceedingsSchema
    
    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default proceedings source format
        """
        try:
	
            return self.ProceedingsSource()
        
	except AttributeError:
        
	    publisher 	 = self.getPublisher()
            address   	 = self.getAddress()
            volume    	 = self.getVolume()
            number       = self.getNumber()
            organization = self.getOrganization()
            series   	 = self.getSeries()
            
	    source = ''
            if publisher: source = ', %s' % publisher
            if address: source += ', ' + address
            if volume: 
		source += ', vol. %s' % volume
		if number: source += '(%s)' % number
	    if organization: source += ', %s' % organization

	    if source: source = source[2:]
	    if series: source += '. %s' % series
	    
            return source + '.'


registerType(ProceedingsReference, PROJECTNAME)
