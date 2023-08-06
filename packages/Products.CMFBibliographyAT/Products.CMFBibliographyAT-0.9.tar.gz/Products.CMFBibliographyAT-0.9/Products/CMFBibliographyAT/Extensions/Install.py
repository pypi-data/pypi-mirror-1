##########################################################################
#                                                                        #
#           copyright (c) 2003-2006 ITB, Humboldt-University Berlin      #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""plone installer script"""

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.MimetypesRegistry import MimeTypeItem

from Products.CMFBibliographyAT.config import *
from Products.CMFBibliographyAT.tool.parsers import *
from Products.CMFBibliographyAT.tool.renderers import *
from Products.CMFBibliographyAT.tool.idcookers import *
from Products.CMFBibliographyAT.migrations import *

# helper methods to be called on tool installation

def addParsers(self):
    """
    helper method to set up a few parsers
    """
    if getattr(self.aq_explicit, 'bibtex', None) is None:
        bibparser = BibtexParser('bibtex')
        self._setObject('bibtex', bibparser)
    if getattr(self.aq_explicit, 'medline', None) is None:
        medparser = MedlineParser('medline')
        self._setObject('medline', medparser)
    if getattr(self.aq_explicit, 'ibss', None) is None:
        ibssparser = IBSSParser('ibss')
        self._setObject('ibss', ibssparser)
    if getattr(self.aq_explicit, 'isbn', None) is None:
        isbnparser = ISBNParser('isbn')
        self._setObject('isbn', isbnparser)
    if getattr(self.aq_explicit, 'endnote', None) is None:
        endparser = EndNoteParser('endnote')
        self._setObject('endnote', endparser)
    if getattr(self.aq_explicit, 'ris', None) is None:
        risparser = RISParser('ris')
        self._setObject('ris', risparser)
    if getattr(self.aq_explicit, 'xml_mods', None) is None:
        xmlparser = XMLParser('xml_mods')
        self._setObject('xml_mods', xmlparser)
    if getattr(self.aq_explicit, 'citationmanager', None) is None:
        citationmanagerparser = CitationManagerParser('citationmanager')
        self._setObject('citationmanager', citationmanagerparser)

def addRenderers(self):
    """
    helper method to set up a few renderers
    """
    id = 'bibtex'
    renderer = BibtexRenderer(id)
    self._setObject(id, renderer)
    renderer.initializeDefaultOutputEncoding(portal_instance=self)
    id = 'endnote'
    renderer = EndRenderer(id)
    self._setObject(id, renderer)
    renderer.initializeDefaultOutputEncoding(portal_instance=self)
    id = 'ris'
    renderer = RISRenderer(id)
    self._setObject(id, renderer)
    renderer.initializeDefaultOutputEncoding(portal_instance=self)
    id = 'pdf'
    renderer = PDFRenderer(id)
    self._setObject(id, renderer)
    renderer.initializeDefaultOutputEncoding(portal_instance=self)
    id = 'xml_mods'
    renderer = XMLRenderer(id)
    self._setObject(id, renderer)
    renderer.initializeDefaultOutputEncoding(portal_instance=self)

def addIdCookers(self):
    """
    helper method to set up a id cookers
    """
    id = 'plone'
    idcooker = PloneIdCooker(id)
    self._setObject(id, idcooker)
    id = 'etal'
    idcooker = EtalIdCooker(id)
    self._setObject(id, idcooker)
    id = 'abbrev'
    idcooker = AbbrevIdCooker(id)
    self._setObject(id, idcooker)
    id = 'uid'
    idcooker = UidIdCooker(id)
    self._setObject(id, idcooker)


# tool installation
def setupTool(self, out):
    """
    adds the bibliography tool to the portal root folder
    """
    if hasattr(self, 'portal_bibliography'):
        self.manage_delObjects(['portal_bibliography'])
        out.write('Deleting old tool; make sure you repeat customizations.')
    addTool = self.manage_addProduct['CMFBibliographyAT'].manage_addTool
    addTool('Bibliography Tool', None)
    out.write("\nAdded the bibliography tool to the portal root folder.\n")
    bibtool = getToolByName(self, 'portal_bibliography')

    prep_server = PREPRINT_SERVERS
    try:
        bibtool.manage_changeProperties({
            'preprint_servers':prep_server,
            },
                                        )
        out.write("Set default properties at the bibliography tool.\n")
    except AttributeError:
        pass

    # add default parsers and renderers
    addParsers(bibtool.Parsers)
    addRenderers(bibtool.Renderers)
    addIdCookers(bibtool.IdCookers)
    out.write(
        "Added default parsers, renderers and id cookers to the bibliography tool.\n")


def addToCatalog(self, out):
    ct = getToolByName(self, 'portal_catalog')

    newFieldIndexes = ['Authors', 'publication_year']
    newSchemaEntries = ['Authors', 'publication_year',
                        'Source', 'citationLabel']
    newKeywordIndexes = ['AuthorItems']

    for idx in newFieldIndexes:
        if idx in ct.indexes():
            out.write("Found the '%s' index in the catalog.\n" % idx)
        else:
            ct.addIndex(idx, 'FieldIndex')
            out.write("Added a field index '%s' to the catalog.\n" % idx)

    for idx in newKeywordIndexes:
        if idx in ct.indexes():
            out.write("Found the '%s' index in the catalog.\n" % idx)
        else:
            ct.addIndex(idx, 'KeywordIndex')
            out.write("Added a keyword index '%s' to the catalog.\n" % idx)

    # DateIndex for the publication_date
    if 'publication_date' not in ct.indexes():
        ct.addIndex('publication_date', 'DateIndex')

    for entry in newSchemaEntries:
        if entry in ct.schema():
            out.write("Found '%s' in the catalog meta data.\n" % entry)
        else:
            ct.addColumn(entry)
            out.write("Added '%s' to the catalog meta data.\n" % entry)

def fixContentTab(self, out):
    pp = getToolByName(self, 'portal_properties', None)
    if pp and hasattr(pp, 'site_properties'):
        use_folder_tabs = pp.site_properties.getProperty('use_folder_tabs', [])
        for ftype in FOLDER_TYPES:
            if ftype not in use_folder_tabs:
                use_folder_tabs += (ftype, )
                pp.site_properties.manage_changeProperties(
                    {'use_folder_tabs' : use_folder_tabs},
                    )

def setFolderWorkflow(self, out):
    wf_tool = getToolByName(self, 'portal_workflow')
    wf_tool.setChainForPortalTypes( FOLDER_TYPES, 'folder_workflow')
    out.write("Made %s subject to 'folder_workflow'.\n" %
              ' and '.join(FOLDER_TYPES))

def addPrefsPanel(self, out):
    cp=getToolByName(self, 'portal_controlpanel', None)
    if not cp:
        out.write("No control panel found. Skipping installation of the setup panel.\n")
    else:
 	cp.addAction(id='BibliographySetup',
                     name='Bibliography Setup',
                     action='string:${portal_url}/prefs_bibliography_docs',
                     permission='Manage portal',
                     category='Products',
                     appId='CMFBibliographyAT',
                     imageUrl='bibliography_tool.png',
                     description='Configure global settings of the bibliography tool.')
        out.write("Installed the bibliography tool configuration panel.\n")
	

def addActions(self, out):
    ap=getToolByName(self, 'portal_actions')

    # Check if the old 'download' action still exists and remove it
    if ap is not None:
        new_actions = [a for a in ap._cloneActions()
                       if a.getId() != 'downloadBib']
        ap._actions = new_actions
    # Add exportBib action to the actions tool
    ## rr: this is still the old way, i.e., name instead of title;
    ## no support for description; permission instead of permissions;
    ## we ought to move to an extension
    ## profile anyway soon so I don't care; it works for now
    ap.addAction(
        id='exportBib',
        name='Export Bibliography',
        action='string:${object_url}/bibliography_exportForm',
        permission='View',
        category='document_actions',
        condition='python:portal.isBibliographyExportable(object)',
        visible=1,
        )

    ap.addAction(
        id='bibliography_search',
        name='Bibliography Search',
        # description='Site wide; sorted by year and authors',
        action='string:${portal_url}/bibliography_search_form',
        permission='View',
        category='portal_tabs',
        condition=None,
        visible=1,
        )

    ai = getToolByName(self, 'portal_actionicons', None)
    if ai is not None:

        # Add the 'export', 'import', and 'pdfdownload' action icons
	ai.addActionIcon('plone','exportBib','bibliography_export.png','Export',0)
	ai.addActionIcon('plone','import','bibliography_import.png','Import',0)
        ai.addActionIcon('plone','download_pdf','bibliography_pdffile.png','Printable file',0)

def changeDefaultViewFor(self, out, type):
    """
    changes the default view for <type> from
    'base_view' to 'bibliographyfolder_view'
    """
    fti = getattr(self.portal_types.aq_base, type, None)
    if not fti: return None
    for a in fti._actions:
        if a.id == 'view':
            a.setActionExpression('bibliographyfolder_view')
            print >> out, \
                  "Changed the %s's default view to" \
                  "'bibliographyfolder_view'." \
                  % type

def fixBibFolderView(self, out):
    """
    checks for the existance of the 'folderlisting' macro in 'base'
    changes the BibFolders's default view if not found
    """
    base_template = getattr(self, 'base', None)
    if base_template is None:
        return None
    macros = getattr(base_template, 'macros', None)
    if macros and 'folderlisting' not in macros.keys():
        changeDefaultViewFor(self, out, 'BibliographyFolder')
        changeDefaultViewFor(self, out, 'LargeBibliographyFolder')

def addCTREntry(self, out):
    """
    add a predicate for 'Bibliography' to the content type registry
    """
    ## make this configurable ???
    predicate_id = 'Bibliography_ext'
    extensions = 'bib, med, end, ris'  # comma separated list
    type_name = 'BibliographyFolder'
    
    ctr = self.content_type_registry
    predicate_ids = [p[0] for p in ctr.listPredicates()]
    if predicate_id not in predicate_ids:
        ctr.addPredicate(predicate_id, 'extension')
        out.write("Adding a '%s' predicate to the content type registry\n"\
                  % predicate_id)
    predicate = ctr.getPredicate(predicate_id)
    predicate.edit(extensions)
    ctr.updatePredicate(predicate_id, predicate, type_name)
    ctr.reorderPredicate(predicate_id, 0)

def install_transform(self, out):
    try:
        print >>out, "Adding new mimetype"
        mimetypes_tool = getToolByName(self, 'mimetypes_registry')
        newtype = MimeTypeItem.MimeTypeItem('HTML with inline citations',
            ('text/x-html-bibaware',), ('html-bib',), 0)
        mimetypes_tool.register(newtype)

        print >>out,"Add transform"
        transform_tool = getToolByName(self, 'portal_transforms')
        try:
            transform_tool.manage_delObjects(['html-to-bibaware'])
        except: # XXX: get rid of bare except
            pass
        transform_tool.manage_addTransform('html-to-bibaware',
                                           'Products.CMFBibliographyAT.transform.html2bibaware')
        if 'bibaware-to-html' not in transform_tool.objectIds():
            transform_tool.manage_addTransform('bibaware-to-html',
                                               'Products.CMFBibliographyAT.transform.bibaware2html')
        addPolicy(transform_tool, out)
    except (NameError,AttributeError):
        print >>out, "No MimetypesRegistry, bibaware text not supported."

def addPolicy(tool, out):
    target = 'text/x-html-safe'
    transform = 'html-to-bibaware'
    policies = tool.listPolicies()
    policy_keys = [p[0] for p in policies]
    if target not in policy_keys:
        print >>out, "Adding transformation policy for bibliographic " \
              "awareness of the 'text/x-html-safe' type."
        tool.manage_addPolicy(target,
                              (transform,),
                              )
    else:
        transforms = [p[1] for p in policies if p[0] == target][0]
        if transform not in transforms:
            transforms += (transform,)
            ## no API for changing a policy :-(
            tool.manage_delPolicies((target,))
            tool.manage_addPolicy(target, transforms)
            print >>out, "Adding the bibliographic transformation to " \
                  "the 'text/x-html-safe' policy."
        else:
            print >>out, "Checked transformation policy"

def autoMigrate(self, out):
    migrations = ( 
	cmfbib07to08.Migration(self, out), 
	cmfbib08to09.Migration(self, out),
    )	
    for migration in migrations:
	migration.migrate()

def install(self):
    out = StringIO()

    # the ActionIcon tool is pretty picky with already existing icons, and easily causes product install
    # to fail with a KeyError: 'Duplicate definition!'. 
    #
    # To avoid this, we try to get rid of all our icons before re-installing them... 
    # 
    removeActionIcons(self)

    setupTool(self, out)
    addPrefsPanel(self, out)
    addActions(self,out)
    addToCatalog(self,out)
    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    install_transform(self, out)
    fixContentTab(self, out)   # for backwards compatibility
    fixBibFolderView(self, out) # for backwards compatibility
    setFolderWorkflow(self, out)
    addCTREntry(self, out)

    autoMigrate(self, out)

    print >> out, "Successfully installed %s's content types." % PROJECTNAME

    return out.getvalue()

# the uninstall need's the following functions

def removePrefsPanel(self):
    cp=getToolByName(self, 'portal_controlpanel', None)
    if cp:
        cp.unregisterApplication('CMFBibliographyAT')

def removeFromActionProviders(self):
    """
    removes portal_bibliography from the action providers
    registered with the action tool
    """
    acttool = getToolByName(self, 'portal_actions')
    if 'portal_bibliography' in acttool.listActionProviders():
        acttool.deleteActionProvider('portal_bibliography')

def removeAction(self):
    """
    removes the export action from the actions tool
    (why doesn't the quickinstaller do that?)
    """
    acttool = getToolByName(self, 'portal_actions')
    actions = list(acttool._actions)
    keep = []
    for a in actions:
        if a.id != 'exportBib':
            keep.append(a)
    acttool._actions = tuple(keep)

def removeActionIcons(self):

    ai = getToolByName(self, 'portal_actionicons')

    # the ActionIcon tool is pretty picky with already existing icons, and easily causes product install
    # to fail with a KeyError: 'Duplicate definition!'. 
    #
    # To avoid this, this function is called on install AND uninstall
    #
    #   o ('plone', 'downloadBib') -> deprecated, has been renamed to exportBib
    #   o ('plone', 'exportBib'), 
    #   o ('plone', 'download_pdf') -> just in case uninstall ai remove failed on product uninstall
    #   o ('controlpanel', 'BibliographySetup') -> in case of an error raised after adding the bibliography 
    #     tool during last product install	
    for category, id in [('plone', 'downloadBib'), ('plone', 'exportBib'), ('plone', 'import'), ('plone', 'download_pdf'), ('controlpanel', 'BibliographySetup'),]:
	try:
    	    ai.removeActionIcon(category,id)
	except KeyError:
    	    pass

def uninstall_transform(self, out):
    transform_tool = getToolByName(self, 'portal_transforms')
    try:
        transform_tool.manage_delObjects(['html-to-bibaware'])
    except:
        pass
    else:
        print >>out, "Transform removed"

def uninstall(self):
    out = StringIO()
    removeFromActionProviders(self)
    removePrefsPanel(self)
    removeActionIcons(self)
    removeAction(self)
    uninstall_transform(self, out)
    # all the rest of the cleaning we leave to quickinstaller
    print >> out, "Uninstalled CMFBibliographyAT."
    return out.getvalue()
