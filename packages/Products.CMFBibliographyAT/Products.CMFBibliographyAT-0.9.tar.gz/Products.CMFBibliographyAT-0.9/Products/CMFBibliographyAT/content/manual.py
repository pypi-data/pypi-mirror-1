##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Manual reference class"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

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
    import organizationField, addressField, editionField


SourceSchema = Schema((
    organizationField,
    addressField,
    editionField,
     ))

ManualSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
               SourceSchema.copy() + TrailingSchema.copy()
ManualSchema.get('authors').required = 0
# normally the publication_year for ManualReferences is optional, but
# in CMFBAT we better force the user to enter something here (better not
# irritate portal_catalog...).
ManualSchema.get('publication_year').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
ManualSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class ManualReference(BaseEntry):
    """ content type to make reference to a manual.
    """
    archetype_name = "Manual Reference"
    source_fields = ('organization', 'address', 'edition',)
    security = ClassSecurityInfo()
    schema = ManualSchema
    
    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default manual source format
        """
        try:

            return self.ManualSource()

        except AttributeError:

	    bs_tool = getToolByName(self, 'portal_bibliostyles', None)
	    address = self.getAddress()
	    edition = self.getEdition()
	    
	    source = ''
	    if address: 
	        source += '%s' % address
		if edition: source += ', '
	    if edition: 
		if bs_tool: source += '%s' % bs_tool.formatEdition(edition, abbreviate=True)
		else: source += '%s ed.' % edition
	    if source and (source[-1] not in  '.?!'): source += '.'

	    return source


registerType(ManualReference, PROJECTNAME)
