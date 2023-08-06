##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Unpublished reference class"""

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import registerType

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry, BaseEntrySchema

UnpublishedSchema = BaseEntrySchema.copy()
UnpublishedSchema.get('authors').required = 1
# YES!!! note is a required field for UnpublishedReferences!!!
UnpublishedSchema.get('note').required = 1
# normally the publication_year for UnpublishedReferences is optional, but
# in CMFBAT we better force the user to enter something here (better not 
# irritate portal_catalog...).
UnpublishedSchema.get('publication_year').required = 1 

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
UnpublishedSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }


class UnpublishedReference(BaseEntry):
    """Content type to make reference to a unpublished document.
    """
    archetype_name = "Unpublished Reference"

registerType(UnpublishedReference, PROJECTNAME)
