##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Inbook reference main class"""

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
    import booktitleField, editorField, publisherField, addressField, \
           editionField, seriesField, chapterField, pagesField

SourceSchema = Schema((
    booktitleField,
    editorField,
    publisherField,
    addressField,
    editionField,
    seriesField,
    chapterField,
    pagesField,
    ))

InbookSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
               SourceSchema.copy() + TrailingSchema.copy()
InbookSchema.get('authors').required = 1
InbookSchema.get('publication_year').required = 1
InbookSchema.get('chapter').required = 1
InbookSchema.get('booktitle').required = 1
InbookSchema.get('pages').required = 1
InbookSchema.get('publisher').required = 1
InbookSchema.get('editor').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
InbookSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class InbookReference(BaseEntry):
    """ content type to make reference to a part/chapter within a book.
    """
    security = ClassSecurityInfo()
    archetype_name = "Inbook Reference"
    source_fields = ('booktitle', 'editor', 'publisher', 'address', 'edition', 'series', 'chapter', 'pages',)

    schema = InbookSchema
    
    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default 'inbook' source format
        """
        try:

            return self.InbookSource()

        except AttributeError:

            booktitle = self.getBooktitle()
            editor    = self.getEditor()
            publisher = self.getPublisher()
            address   = self.getAddress()
            chapter   = self.getChapter()
            pages     = self.getPages()
            
            source = 'In: %s' % booktitle
            
            if editor: source += ', ed. by %s' % editor
            if publisher: source += '. ' + publisher
            if address: source += ', ' + address
            if chapter: source += ', chap. %s' % chapter
            if pages: source += ', pp. %s' % pages
            
            return source + '.'


registerType(InbookReference, PROJECTNAME)
