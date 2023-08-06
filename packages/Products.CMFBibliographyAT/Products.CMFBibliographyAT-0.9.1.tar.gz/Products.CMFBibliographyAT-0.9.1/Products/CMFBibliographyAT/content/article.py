##########################################################################
#                                                                        #
#           copyright (c) 2003, 2005 ITB, Humboldt-University Berlin     #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Article reference main class"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField, StringWidget
#    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import registerType

from Products.CMFBibliographyAT.marshall import BibtexMarshaller
from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import journalField, volumeField, numberField, pagesField


SourceSchema = Schema((
    journalField,
    volumeField,
    numberField,
    pagesField,
    StringField('pmid',
	is_duplicates_criterion=True,
        widget=StringWidget(label="PubMed ID",
            label_msgid="label_pmid",
            description="The reference's number in the PubMed database.",
            description_msgid="help_pmid",
            i18n_domain="cmfbibliographyat",
	),
    ),
    StringField('DOI',
	is_duplicates_criterion=True,
        widget=StringWidget(label="DOI",
            label_msgid="label_doi",
            description="The reference's digital object identifier.",
            description_msgid="help_doi",
            i18n_domain="cmfbibliographyat",
	),
    ),
))

ArticleSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                SourceSchema.copy() + TrailingSchema.copy()
ArticleSchema.get('authors').required = 1
ArticleSchema.get('publication_year').required = 1
ArticleSchema.get('journal').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
ArticleSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class ArticleReference(BaseEntry):
    """ content type to make reference to a (scientific) article.
    """
    security = ClassSecurityInfo()
    archetype_name = "Article Reference"
    source_fields = ('journal', 'volume', 'number', 'pages', 'pmid',)

    schema = ArticleSchema
    
    security.declareProtected(View, 'PMID')
    def PMID(self):
        """ returns the pmid if set
        """
        value = self.getPmid()
        if value:
            return value
        else:
            return None
        
    security.declareProtected(View, 'getPubMedLink')
    def getPubMedLink(self, defaultURL=None):
        """ a link to PubMed
            if pmid is set or the default otherwise
        """
        if self.getPmid():
            url = "http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve"
            return url + "&db=PubMed&list_uids=%s" % self.getPmid()
        else: return defaultURL

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default article source format
        """
        try:
            return self.ArticleSource()
        except AttributeError:
            journal = self.getJournal()
            volume  = self.getVolume()
            number  = self.getNumber()
            pages   = self.getPages()
            source = ''
            if journal:
                source += journal
            if volume:
                source += ', %s' % volume
            if number:
                source += '(%s)' % number
            if pages:
                source += ':%s' % pages
            return source + '.'

registerType(ArticleReference, PROJECTNAME)
