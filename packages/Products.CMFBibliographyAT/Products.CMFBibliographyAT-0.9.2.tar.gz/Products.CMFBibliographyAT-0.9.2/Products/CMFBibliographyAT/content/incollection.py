##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Incollection reference main class"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import registerType

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.inbook import InbookReference
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import booktitleField, editorField, volumeField, numberField, \
	   typeField, publisherField, addressField, \
           editionField, seriesField, chapterField, pagesField
								      
SourceSchema = Schema((
    booktitleField,
    editorField,
    volumeField,
    numberField,
    typeField,
    publisherField,
    addressField,
    editionField,
    seriesField,
    chapterField,
    pagesField,
))
				    
IncollectionSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
        	     SourceSchema.copy() + TrailingSchema.copy()
IncollectionSchema.get('authors').required = 1
IncollectionSchema.get('publication_year').required = 1
IncollectionSchema.get('booktitle').required = 1
IncollectionSchema.get('publisher').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
IncollectionSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class IncollectionReference(InbookReference):
    """ content type to make reference to a chapter within a collection volume.
    """
    security = ClassSecurityInfo()
    source_fields = ('booktitle', 'editor', 'volume', 'number', 'publication_type', 'publisher', 'address', 'edition', 'series', 'chapter', 'pages',)

    archetype_name = "Incollection Reference"
    schema = IncollectionSchema

    security.declareProtected(View, 'Source')
    def Source(self):
	""" the default 'incollection' source format
	"""
	try:

    	    return self.IncollectionSource()

	except AttributeError:

            booktitle 	     = self.getBooktitle()
	    editor    	     = self.getEditor()
            volume    	     = self.getVolume()
            number    	     = self.getNumber()
            publication_type = self.getPublication_type()
            publisher 	     = self.getPublisher()
    	    address   	     = self.getAddress()
	    chapter   	     = self.getChapter()
	    pages     	     = self.getPages()
	    series     	     = self.getSeries()
    
    	    source = 'In: %s' % booktitle
            if editor: source += ', ed. by %s' % editor
	    if volume: 
    		source += ', vol. %s' % volume
                if number: source += '(%s)' % number
            if chapter: source += ', chap. %s' % chapter
    	    if pages: source += ', pp. %s' % pages
	    if publisher: source += ', ' + publisher
    	    if address: source += ', ' + address
	    if publication_type: source += ', %s' % publication_type   
    
	    if source and (source[-1] not in '.!?'): source += '.'
    
	    if series: source += ' %s.' % series
	    
	    return source

registerType(IncollectionReference, PROJECTNAME)
