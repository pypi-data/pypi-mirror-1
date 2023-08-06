##########################################################################
#                                                                        #
#           copyright (c) 2003 - 2006 ITB, Humboldt-University Berlin    #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""BaseEntry: base class for bibliographic references;
defines the common schema elements and provides some
basic functionality """

import string, types
from DateTime import DateTime
from ZPublisher.HTTPRequest import FileUpload
from Acquisition import aq_base, aq_inner, aq_parent
from ComputedAttribute import ComputedAttribute
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, ModifyPortalContent, \
     ManageProperties, AddPortalContent
from Products.CMFCore.utils import getToolByName

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import BaseContent
else:
    from Products.Archetypes.public import BaseContent

from Products.Archetypes.public import DisplayList
from Products.Archetypes.Renderer import renderer
from Products.Archetypes.Schema import getNames
from Products.Archetypes.utils import shasattr
# try ATCT
from Products.ATContentTypes.content.base \
    import ATCTContent as BaseContent
     
from Products.ATContentTypes.content.base \
    import cleanupFilename

from Products.CMFBibliographyAT.interfaces import IBibliographyExport

from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema

from Products.CMFBibliographyAT.utils import _encode, _decode

BaseEntrySchema = HeaderSchema + \
                  AuthorSchema + \
                  CoreSchema + \
                  TrailingSchema

class BaseEntry(BaseContent):
    """Base content for bibliographical references content types
    """
    global_allow = 0
    content_icon = 'bibliography_entry.png'
    immediate_view = 'bibliography_entry_view'
    default_view = 'bibliography_entry_view'
    suppl_views    = ('bibliography_entry_view',
                      'base_view',
                      'table_view',
                      )

    schema = BaseEntrySchema
    _at_rename_after_creation = True
    
    __implements__ = (BaseContent.__implements__,
                      IBibliographyExport,
                     )
    security = ClassSecurityInfo()
    
    actions = (
        {
        'id'            : 'view',
        'name'          : 'View',
        'action'        : 'string:${object_url}/bibliography_entry_view',
        'permissions'   : (View,),
        'category'      : 'object',
        },
        {
        'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'string:${object_url}/edit',
        'permissions'   : (ModifyPortalContent,),
        },
        {
        'id'            : 'local_roles',
        'name'          : 'Sharing',
        'action'        : 'string:${object_url}/folder_localrole_form',
        'permissions'   : (ManageProperties,),
	'condition'     : 'python: object.portal_membership.checkPermission("Manage Properties", object)',
        },
        {
        'id'            : 'import',
        'name'          : 'Import Bibliography',
        'action'        : 'string:${folder_url}/bibliography_importForm',
	'condition'     : 'python: object.portal_membership.checkPermission("Add portal content", object.getBibFolder())',
        'permissions'   : (AddPortalContent,),
        'category'      : 'document_actions',
        },
        {
        'id'            : 'download_pdf',
        'name'          : 'Printable file (PDF)',
        'action'        : 'python:"%s" % object.download_pdf()',
        'permissions'   : (View,),
        'condition'     : 'object/has_pdf',
        'category'      : 'document_actions',
        },
    )
    aliases = {
        '(Default)'     : '(dynamic view)',
        'view'          : '(selected layout)',
        'index.html'    : '(dynamic view)',
        'edit'          : 'base_edit',
        'properties'    : 'base_metadata',
        'sharing'       : 'folder_localrole_form',
        'gethtml'       : '',
        'mkdir'         : '',
    }

    # the default source
    security.declareProtected(View, 'Source')
    def Source(self):
        """
        the default source format
        """
        try:
            source = self.DefaultSource()
        except AttributeError:   # don't blow if we have no skin context
            source = self.portal_type
        return source

    security.declareProtected(View, 'isTranslatable')
    def isTranslatable(self):
    
        bib_tool = getToolByName(self, 'portal_bibliography')
        plone_utils = getToolByName(self, 'plone_utils')
        return bib_tool.isBibrefItemTranslatable() and plone_utils.isTranslatable(self)

    security.declareProtected(View, 'getCookIdWarning')
    def getCookIdWarning(self, **kwargs):
        try:
            return self.getId(**kwargs)
        except TypeError:
            return self.getId()
	
    security.declareProtected(View, 'getReferenceTypes')
    def getReferenceTypes(self):
    
        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.getReferenceTypes()

    
    security.declareProtected(View, 'getAbstract')
    def getAbstract(self, html_format=False, **kw):
        """ get the 'description' and put it in the 'abstract'
        """
        if not html_format:
            return self.Description(**kw)
        
        # this is for dynamic migration: in v0.8 description and abstract were the same field (description)
        # in > v0.9 'abstract' stores the html abstract, 'description' the plain text abstract.
        if not self.Schema()['abstract'].get(self, **kw) and self.Description(**kw):
            return self.Description(**kw)
        
        return self.Schema()['abstract'].get(self, **kw)
        
    security.declareProtected(View, 'editAbstract')
    def editAbstract(self, **kw):
        """ get the 'description' and put it in the 'abstract'
        """
        return self.getAbstract(html_format=True, raw=True, **kw)
        
    security.declareProtected(ModifyPortalContent, 'setAbstract')
    def setAbstract(self, val, **kw):
        """ synchronize 'abstract' and 'description'
        """
        tr_tool = getToolByName(self, 'portal_transforms')
        plain = tr_tool.convertTo('text/plain', val)
        self.setDescription(plain.getData().replace('\r\n', ' ').replace('\n\r', ' ').replace('\r', ' ').replace('\n', ' ').strip())
        self.Schema().getField('abstract').set(self, value=val, **kw)

    # helper method for direct attribute access
    # !! Should not be called anymore since Archetypes
    # !! builds automatic getFieldName() methods
    # rr: still needed by the bibtex renderer

    def getFieldValue(self, field_name):
        """
        get a field's value
        """
        field = self.getField(field_name)
        value = getattr(self, field.accessor)()
        if value:
            return value
        else:
            try:
                return field.getDefault()
            except TypeError:
                # AT1.3 compliant
                return field.getDefault(self)

    # custom methods for author handling
    security.declareProtected(View, 'getAuthorList')
    def getAuthorList(self):
        """
        returns the list of author dictionaries for editing
        assumes attribute storage for authors

        Deprecated; use default accessor instead
        """
        return self.getAuthors()

    security.declareProtected(View, 'AuthorItems')
    def AuthorItems(self, format="%L %f"):
        """
        returns a list of author strings, e.g.,
        ["Foo J", "Bar B"]
        useful for being indexed with a keyword index
        """
        return [a(format) for a in self.getAuthors()]    

    security.declareProtected(View, 'Authors')
    def Authors(self, *args, **kwargs):
        """Alias for the publication author's accessor
        with a custom default format ("%L, %f%m") if not specified"""
        if 'format' not in kwargs.keys():
            kwargs['format'] = "%L, %f%m"
        return self.getAuthors()(*args, **kwargs)

    security.declareProtected(View, 'getAuthorURL')
    def getAuthorURL(self, author):
        """
        finds the URL of the author's hompage
        First, looks if 'homepage' is set in the 'author' dictionary
        Second, asks the tool for an entry for 'firstname' + 'lastname'
        Third, asks the membership tool whether there is a user 'lastname'
        """
        # 1. on object base
        homepage = author.get('homepage', None)
        if homepage: return homepage

        # 2. on bibfolder base
        parent = self.getBibFolder()
        full_name = author.get('firstname', '') \
                    + ' ' \
                    + author.get('lastname', '')

        if parent.meta_type == 'BibliographyFolder':
            homepage = parent.AuthorURLs().get(full_name.strip(), None)
        if homepage: return homepage

        # 3. Site wide look-up by fullname
        membertool = getToolByName(self, 'portal_membership', None)
        full_names = [m.getProperty('fullname', 'dummy') \
                      for m in membertool.listMembers()]
        try:
            index = full_names.index(full_name)
            user = membertool.listMembers()[index].getId()
            return membertool.getHomeUrl(user, 1)
        except ValueError:
            pass

        # 4. Site wide look-up by first initial plus lastname

        fname = author.get('firstname', '')
        lname = author.get('lastname', '')
        abbrev_name = ''
        if fname: abbrev_name += fname + ' '
        abbrev_name += lname
        abbrev_name = abbrev_name.strip()

        abbrev_names = []
        for name in full_names:
            tokens = name.split()
            if len(tokens) > 1:
                aname = tokens[0][0] + ' ' + tokens[-1]
            else:
                aname = name
            abbrev_names.append(aname)
        try:
            index = abbrev_names.index(abbrev_name)
            user = membertool.listMembers()[index].getId()
            return membertool.getHomeUrl(user, 1)
        except ValueError:
            pass


        # 5. admittedly stupid default
        user = author.get('lastname', '').lower()
        homepage = membertool.getHomeUrl(user, 1)

        return homepage

    security.declareProtected(View, 'getURL')
    def getURL(self, defaultURL=None, relative=None, remote=False):
        """
        the publication_url if set, otherwise a link to PubMed
        if pmid is set, the default if not None or the item's
        absolute_url otherwise except if relative equals 1
        in which case the items relative url is obtained from
        the portal_url tool.
        """
        if relative==1:
            # called from folder_contents and friends
            utool = getToolByName(self, 'portal_url')
            return utool.getRelativeContentURL(self)
        url = self.getPublication_url()
        if url:
            return url
        elif not remote:
            return defaultURL or self.absolute_url()
        else:
            return defaultURL

    security.declareProtected(View, 'PMID')
    def PMID(self):
        """
        to be available for all types
        overwritten by article
        """
        return None

    security.declareProtected(View, 'ISBN')
    def ISBN(self):
        """
        to be available for all types
        overwritten by books
        """
        return None

    security.declareProtected(View, 'pre_validate')
    def pre_validate(self, REQUEST, errors):

	at_tool = getToolByName(self, 'archetype_tool')

        authors = REQUEST.get('authors',[])
        result = []
        references=[]
	
	# deduce author names from member reference
        for author in authors:
            reference = author.get('reference', None)
            if reference == 'None':
                author.reference = ''
            elif reference:
            
	    	reference_object = at_tool.lookupObject(reference)
                if reference_object.isTranslatable():
                    references.append(reference_object.getCanonical().UID())
                    reference_object = reference_object.getCanonical()
                else:
                    references.append(reference)    
                
                # obtain author data from privileged fields in the reference object
                data = self.getAuthorDataFromMember(reference_object)
		only_requested_data = not not author.get('lastname', None)
		if data:
		    for key in [ key for key in data.keys() if key not in ('middlename',) ]:
			if not only_requested_data or (author.get(key, None) == '?'):
			    if key == 'firstname':
				author.firstnames = _decode(data['firstname']) + ' ' + _decode(data['middlename'])
			    else:
				exec('author.%s = _decode(data[key])' % key)
                    
                # if this doesn't help, we try to derive the author name from the Title of reference... (YUK)
                if not author.get('lastname', None):
                    firstnames, lastname = self._name_from_reference(reference)
                    author.firstnames = firstnames
                    author.lastname = lastname
            
            if ''.join([_decode(_encode(val)) for val in dict(author).values()]).strip():
                result.append(author)
                
        REQUEST.form['authors'] = result[:]
        REQUEST.form['member_publication_authors'] = references[:]

    def _name_from_reference(self, uid):
        catalog = getToolByName(self, 'uid_catalog', None)
        if catalog is None:
            return ('','')
        brains = catalog(UID=uid)
        if not brains:
            return ('','')
        parts = brains[0].Title.split()
        first = ''.join(parts[:-1]).strip()
        last = parts[-1]
        return first, last

    # try to set author references, e.g., after uploads
    security.declareProtected(ModifyPortalContent, 'inferAuthorReferences')
    def inferAuthorReferences(self, report_mode='v', is_new_object=False):
        """
        If the item has no author references set but the tool supports
        member references or the site uses CMFMember, it tries to find 
	a content object corresponding to the author name and makes 
	reference there.
        
        Lookup is done on firstname lastname match.
        
        A report is returned controlled by the mode:

        - 'v': verbose; the default; for each author it is indicated
               what was done.
        - 'q': quiet; nothing is returned
        - 'c': conflicts only; conflicts occur if several potential
               target members are found
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        if not self.showMemberAuthors():
            return "No inference attempted"
        report = []
        authors = []
        a_modified = False
        md = getToolByName(self, 'portal_memberdata')
        m_tool = getToolByName(self, 'portal_membership')
        membertypes = bib_tool.getMemberTypes() or \
                      md.getAllowedMemberTypes()
        catalog = getToolByName(self, 'portal_catalog')
        first_inferred_author = True
        for author in self.getAuthors():
            authors.append(author)
            lastname = author.get('lastname', None)
            firstnames = author.get('firstnames', None)
            if lastname is None:
                continue
	    
	    raw_candidates = ()
	    search_order = (bib_tool.getMembersSearchOnAttr(), 'Title',)
	    for search_on in search_order:
		if search_on:
		    raw_candidates = eval("catalog({'portal_type': membertypes, '%s': lastname,})" % search_on)

		    candidates = []
		    for cand in raw_candidates:
			try:
			    candidate_accessor = eval('cand.getObject().%s' % search_on)
			    if callable(candidate_accessor):
				candidate_name = candidate_accessor()
	    		    else:
				candidate_name = str(candidate_accessor)	
			    if string.find(candidate_name, ', ') != -1:
	    			candidate_lastname = candidate_name.split(', ')[0]
				candidate_firstnames = ' '.join(candidate_name.split(', ')[1:])
    			    else: 
				candidate_lastname = candidate_name.split(' ')[-1]
				candidate_firstnames = ' '.join(candidate_name.split(' ')[:-1])
			    if (lastname == candidate_lastname) and (firstnames == candidate_firstnames):
				candidates.append(cand)
				break
			
			except AttributeError:
			    # cand.getObject does not have the attribute requested in bib_tool.getSelectMembersAttr()
			    # skip this candidate
			    pass

		    if candidates: break
	    
	    if not candidates:
                msg = "%s: no corresponding member found." % author()
                if report_mode == 'v':
                    report.append(msg)
            elif len(candidates) > 1:
                msg = "%s: several corresponding members found:" % author()
                for c in candidates:
                    msg += " %s at %s," % (c.Title, c.getURL(relative=1))
                report.append(msg)
            else:
                select_attr = bib_tool.getSelectMembersAttr()
                target = candidates[0].getObject()
                
                # we will prefer the canonical if we have to deal with a translated object
                if target.isTranslatable():
                    target = target.getCanonical()
                    
                author['reference'] = target.UID()
                self.addReference(target, 'authorOf')
                
                # obtain author data from privileged fields in the target object
                data = self.getAuthorDataFromMember(target)
                target_givenName = _encode(_decode(data['firstname']) + ' ' + _decode(data['middlename']))
                target_lastName = _encode(_decode(data['lastname']))

                # also prepare for a failure of getAuthorDataFromMember
                select_attr_name = bib_tool.getSelectMembersAttr()
                if select_attr_name:
                    select_attr = getattr(target, select_attr_name, None)
                else:
                    select_attr = None
                if callable(select_attr):
                    name = select_attr() or target.Title()
                else:
                    name = select_attr or target.Title()

                # this is for member name information stored in explicit fields in
                # the member target object
                if \
                   \
                   (author['lastname'] == target_lastName) and \
                   (target_givenName.startswith(author['firstname'])):
                   
                        # we have found a target / author match
                        pass
                   
                # this for name pattern "FIRSTNAMES LASTNAME" \
                elif \
                     \
                   (len(name.split(', ')) == 1) and \
                   name.startswith(author.get('firstname')) and \
                   name.endswith(author.get('lastname')):
                   
                        # we have found a target / author match
                        pass

                # this for name pattern "LASTNAME, FIRSTNAMES" \
                elif \
                     \
                   (len(name.split(', ')) == 2) and \
                   name.startswith(author.get('lastname')) and \
                   ( name.endswith(author.get('firstname')) or \
                     name.endswith(author.get('firstname') + ' ' + author.get('middlename'))):
                
                        # we have found a target / author match
                        pass
                            
                else:            
                
                    # bad luck, author / member_type data mismatch 
                    msg = "%s: no corresponding member found." % author()
                    continue
                
                if shasattr(target, 'getMemberId'): memberId = target.getMemberId()
                else: memberId = target.getId()
                if m_tool.getMemberInfo(memberId):
		
		    if bib_tool.authorOfImpliesOwner:
		    
                        # assign the member ids as owner    
                        self.bibliography_entry_addOwnerToLocalRoles(memberId=memberId)
			if self.getBibFolder().getSynchronizePdfFileAttributes():
    			    self.bibliography_pdffile_addOwnerToLocalRoles(memberId=memberId)
			
                    if bib_tool.authorOfImpliesCreator():
		    
                        # also write the member ids to the creator metadata field.    
                        #try:
                            if first_inferred_author: 
                                creators = []
                                first_inferred_author = False
                            else:    
                                creators = list(self.listCreators())
                                
                            if memberId not in creators:
                                creators.append(memberId)

                            self.setCreators(value=tuple(creators))
			    pdf_file = self.getPdf_file()
			    if pdf_file and self.getBibFolder().getSynchronizePdfFileAttributes():
			    
				pdf_file.setCreators(value=tuple(creators))
				
                        #except AttributeError:
                        #    pass    
                
                a_modified = True
                msg = "%s: referring to %s at %s." \
                      % (author(),
                         name,
                         target.absolute_url(relative=1),
                         )
                if report_mode == 'v':
                    report.append(msg)

        if a_modified and not is_new_object:
            self.setAuthors(authors)
            self.reindexObject()
        if report_mode != 'q' and report:
            ## report.insert(0, "%s:\n" % self.absolute_url(relative=1))
            return ' '.join(report)    
        return None

    security.declareProtected(View, 'getPublicationDate')
    def getPublicationDate(self):
        """
        Returns the publication date as DateTime
        or None if it is not well defined
        """
        year = self.getField('publication_year').get(self)
        try:
            year = int(year)
        except ValueError:
            year = None

        month = self.getField('publication_month').get(self)
        if month:
            try:
                month = int(month)
            except ValueError:
                try:
                    # This is probably a string
                    monthcomp = month.split(' ')
                    month = 1
                    for m in monthcomp:
                        if m.lower() in DateTime._monthmap.keys():
                            month = m
                            continue
                except (ValueError, AttributeError, IndexError):
                    month = 1
        else:
            month = 1

        return year and DateTime('%s/%s/01' % (year, month)) or None

    publication_date = ComputedAttribute(getPublicationDate, 1)

    # PDF support stuff
    security.declareProtected(View, 'widget')
    def widget(self, field_name, mode='view', field=None, **kwargs):
	""" special handling for uploaded_pdfFile widget
	"""
        bib_tool = getToolByName(self, 'portal_bibliography')
	pdf_file = self.getPdf_file()
	if (pdf_file and self.isPdfUploadAllowedForThisType() and bib_tool.allowPdfUploadPortalPolicy()) and ((field_name == 'uploaded_pdfFile') or (field == self.Schema().getField('uploaded_pdfFile'))):
	
	    if pdf_file:	
		field_name = 'uploaded_pdfFile'
		if field is None:
		    field = pdf_file.Schema()['file']
		widget = field.widget
		return renderer.render(field_name, mode, widget, pdf_file, field=field, **kwargs)    
	    
	else:

            return BaseContent.widget(self, field_name=field_name, mode=mode, field=field, **kwargs)
    
    security.declareProtected(View, 'getPdfFolderPath')
    def getPdfFolderPath(self):
        """path to the pdfs folder in the parent bib-folder"""
        url_tool = getToolByName(self, 'portal_url')
        pdff = self.getBibFolder().getPdfFolder() 
        return url_tool.getRelativeContentURL(pdff)
    
    security.declareProtected(AddPortalContent, 'setUploaded_pdfFile')
    def setUploaded_pdfFile(self, value=None, **kwargs):
	"""create PDF file in PDF folder on-the-fly"""
	bib_tool = getToolByName(self, 'portal_bibliography')
	types_tool = getToolByName(self, 'portal_types')
	bibfolder = self.getBibFolder()
	pdf_file = self.getPdf_file()
	if not pdf_file and isinstance(value, FileUpload):
    	
	    pdf_folder = bibfolder.getPdfFolder()

	    # create PDF file and associate reference with it
	    file_field = self.getField('uploaded_pdfFile')

	    if bibfolder.getSynchronizePdfFileAttributes():
	
		pdf_file_id = self.getId() + '.pdf'    
	    
	    else:    
		file_field.getFilename(self, fromBaseUnit=False)
		file_field.getFilename(self, fromBaseUnit=True)

		try:
			# Plone 2.X
			pdf_file_id = cleanupFilename(context=self, 
										  filename=value.filename,  
										  encoding=self.getCharset())
		except TypeError:
			# Plone 3.X
			pdf_file_id = cleanupFilename(value.filename, self.REQUEST) 
	    
	    # temporarily allow PDF File creation in PDF Folder, create PDF File, revoke PDF File creation allowance
	    pdf_folder.allowPdfFileCreation()
	    new_id = pdf_folder.invokeFactory(id=pdf_file_id, type_name='PDF File', )
	    pdf_folder.disallowPdfFileCreation()
	    	    
	    # find the PDF File's ID and get the object
	    if new_id is None or (new_id == ''):
		new_id = pdf_file_id
	    pdf_file = pdf_folder._getOb(id=new_id)
	    
	    # set the file value
	    pdf_file.setFile(value, **kwargs)
	    if pdf_file:
			self.setPdf_file(value=pdf_file.UID())

	elif pdf_file and isinstance(value, FileUpload):
	    ## replace file field in PDF file
	    pdf_file.setFile(value, **kwargs)
	    
	elif pdf_file and isinstance(value, basestring) and (value == 'DELETE_FILE'):

	    pdf_folder = bibfolder.getPdfFolder()
	    ## delete PDF file, delete PDF file reference
	    pdf_folder.manage_delObjects(ids=[pdf_file.getId()])
	    self.setPdf_file(value=None)
	
    security.declareProtected(View, 'getUploaded_pdfFile')
    def getUploaded_pdfFile(self, **kwargs):
    	""" retrieve pdf document from associated pdf file
	"""
        bib_tool = getToolByName(self, 'portal_bibliography')
	pdf_file = self.getPdf_file()
	if (pdf_file is not None) and self.isPdfUploadAllowedForThisType() and bib_tool.allowPdfUploadPortalPolicy():
	    return pdf_file.Schema()['file'].getBaseUnit(pdf_file, **kwargs)
	else:
	    return None
    
    security.declareProtected(View, 'editUploaded_pdfFile')
    def editUploaded_pdfFile(self, **kwargs):
    	""" retrieve pdf document from associated pdf file for editing
	"""
	return self.getUploaded_pdfFile(**kwargs)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):

	# manage_beforeDelete is deprecated in Zope 2.11+
	
	### remove associated PDF file if any
	###
	### BEWARE: to debug this code go into portal_skins/plone_scripts/object_delete and comment out the 
	###         fallback exception or use PloneTestCase
	###
	
	bibfolder = self.getBibFolder()

	# delete PDF file (if any) only if _delete_associated_pdffile flag in bibfolder is set
	pdf_file = self.getPdf_file()
	if pdf_file:
	    if bibfolder._delete_associated_pdffiles:

		bibfolder = self.getBibFolder()
    	        pdf_folder = bibfolder.getPdfFolder()
		pdf_file = self.getPdf_file()
		pdf_folder.manage_delObjects(ids=[pdf_file.getId()])
		bibfolder._delete_associated_pdffiles = False

	    if bibfolder._move_associated_pdffiles:
		
		setattr(item, '_temp_pdffile_UID', pdf_file.UID())
		
	BaseContent.manage_beforeDelete(self, item, container)
	
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
    
	# manage_afterAdd is deprecated in Zope 2.11+
	
	### copy PDF file if bibreference has been copied
	
	###
	### BEWARE: to debug this code go into portal_skins/plone_scripts/folder_paste and comment out the 
	###         fallback exception or use PloneTestCase
	###
	
	at_tool = getToolByName(self, 'archetype_tool')
	bib_tool = getToolByName(self, 'portal_bibliography')
    	bibfolder = container

	# grab the PDF file and its back references before the reference is removed by 
	# BaseContent.manage_afterAdd
    	pdf_file = self.getPdf_file() or None
	pdf_file_uid = ''
	if pdf_file:
	    pdf_file_uid = pdf_file.UID()
	    pdf_file_brefs = [ bref.UID() for bref in pdf_file.getBRefs('printable_version_of') if bref is not None ]

	if not pdf_file_uid and shasattr(self, '_temp_pdffile_UID') and self._temp_pdffile_UID:
	    pdf_file_uid = self._temp_pdffile_UID
	    pdf_file_brefs = [ bref.UID() for bref in at_tool.lookupObject(pdf_file_uid).getBRefs('printable_version_of') if bref is not None ]
	    delattr(self, '_temp_pdffile_UID')

	# first do all necessary ATCT, Archetypes, etc. things...
	BaseContent.manage_afterAdd(self, item, container)
	
	# we have to set another transaction savepoint here, before we can cut or copy the associated PDF file
	bib_tool.transaction_savepoint(optimistic=True)
	
	# then check PDF file association
	pdf_file = pdf_file_uid and at_tool.lookupObject(pdf_file_uid)
	if pdf_file and pdf_file_brefs and (self.UID() not in pdf_file_brefs):
		
	    # bibref item has been copied and UID of bibref item has changed
	    # => copy PDF file
    	    new_pdf_file = self.relocatePdfFile(pdf_file=pdf_file, op=0)
    	    self.setPdf_file(value=new_pdf_file.UID())
		
	elif pdf_file and (pdf_file.aq_inner.aq_parent.aq_inner.aq_parent.getPhysicalPath() != self.aq_inner.aq_parent.getPhysicalPath()):
	
	    # PDF file and bibref item are not in the same bibfolder
	    # => move PDF file!!!
	    moved_pdf_file = self.relocatePdfFile(pdf_file=at_tool.lookupObject(pdf_file_uid), op=1)
	    
    security.declareProtected(AddPortalContent, 'relocatePdfFile')
    def relocatePdfFile(self, pdf_file=None, bibfolder=None, op=1):
	""" find associated PDF File and move into correct PDF Folder
	    --> used for manage_cutObjects -> manage_pasteObjects
	    --> used if PDF Folder is inconsistent
	    op == 0: copy operation
	    op == 1: move operation (default)
	"""     
	bib_tool = getToolByName(self, 'portal_bibliography')

    	bibfolder = bibfolder or self.getBibFolder()
	pdf_file = pdf_file or self.getPdf_file()
	
	new_pdf_file = None
	if pdf_file:
	
	    pdf_folder = bibfolder.getPdfFolder()
	    if (pdf_file not in pdf_folder.contentValues()) or (op==0):
	    
    		pdf_file_id = pdf_file.getId()
	
		# we need to explicitly add 'PDF File' content type as allowed type to 'PDF Folder' content type
		pdf_folder.allowPdfFileCreation()
	    	    
		# if the edit action was cut+paste, we will copy the PDF file here anyway. In case of cut+past it 
		# will be deleted by self.manage_beforeDelete.
		if op == 0: pdf_objs = pdf_file.aq_inner.aq_parent.manage_copyObjects([pdf_file_id])
		elif op == 1: pdf_objs = pdf_file.aq_inner.aq_parent.manage_cutObjects([pdf_file_id])
		result = pdf_folder.manage_pasteObjects(pdf_objs)

		# restore PDF Folder's allowed content types
		pdf_folder.disallowPdfFileCreation()
	
		# get the new PDF file
		new_pdf_file_id = [ res['new_id'] for res in result if res['id'] == pdf_file_id ][0]
		new_pdf_file = pdf_folder._getOb(new_pdf_file_id)
	
		# set field values of the new PDF file
		if bibfolder.getSynchronizePdfFileAttributes():
		    self.bibliography_pdffile_cookId()
		    
	if new_pdf_file:	    
	    # make sure our new PDF file gets seen by the portal's catalog tool
	    new_pdf_file.reindexObject()	
	    return new_pdf_file	    

    security.declareProtected(View, 'isPdfUploadAllowedForThisType')
    def isPdfUploadAllowedForThisType(self):
    
        bib_folder = self.getBibFolder()
        return self.portal_type in bib_folder.getAllowPdfUploadForTypes()

    security.declareProtected(View, 'download_pdf')
    def download_pdf(self):
        """
        Returns the URL of the printable (pdf) file.
        
        Used by the download printable action
        """
        bib_tool = getToolByName(self, 'portal_bibliography')

        # for the case that people have already uploaded files and 
        # policy changed later we have to assume that PDF files are 
        # already there and shall be hidden after the setup of a more
        # restricted policy.
        if bib_tool.allowPdfUploadPortalPolicy():
    	    
            if self.isPdfUploadAllowedForThisType():        
    
                pdf_file = self.getPdf_file()
	        if pdf_file:
                    return pdf_file.absolute_url()
	    
        pdf_url = self.getPdf_url()
        if pdf_url:
            return pdf_url
        return None

    security.declareProtected(View, 'has_pdf')
    def has_pdf(self):
        """Used by the download printable action condition"""
        return self.download_pdf() and True or False

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        """Make sure our dependend gets cataloged as well"""

        pdf_file = self.getPdf_file()
        if pdf_file:
            pdf_file.reindexObject()
            
    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
	"""override Archetype's _renameAfterCreation method with CMFBAT's ID cooker
	"""
	# cook id on object creation
	bib_tool = getToolByName(self, 'portal_bibliography')
	plone_utils = getToolByName(self, 'plone_utils')
	bibfolder = self.getBibFolder()
	if bibfolder.getCookIdsOnBibRefCreation() and check_auto_id and plone_utils.isIDAutoGenerated(self.getId()):
	    # leave the job to the at_post_edit_script, id cooking on creation cannot happen here
	    # as the formattablenames fields set the at_creation_flag to False when the "More" button is used
	    # so we have to cook IDs on post-create and post-edit...
	    pass

	else:

	    # id cooking? not specifically enabled? use auto generated IDs
	    pass
	    
    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
    
	self.at_post_edit_script()
	
    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
    	    
	bib_tool = getToolByName(self, 'portal_bibliography')
	plone_utils = getToolByName(self, 'plone_utils')
	bibfolder = self.getBibFolder()
	
	# id cooking 
	if (bibfolder.getCookIdsOnBibRefCreation() and plone_utils.isIDAutoGenerated(self.getId())) or bibfolder.getCookIdsAfterBibRefEdit():
    	    new_id = bib_tool.cookReferenceId(ref=self, idcooker_id=bibfolder.getReferenceIdCookingMethod())
	    if new_id != 'nobody1000':
	    
		# this will implicitly call the PDF File rename code via self.manage_renameObject
		self.bibliography_entry_cookId()
		
	    else:
		# no author, no publication year, do not know what to do
		BaseContent._renameAfterCreation(self, check_auto_id=True)
		
	# infer member references after edit
	if bib_tool.inferAuthorReferencesAfterEdit():
	    self.inferAuthorReferences()
	    
    security.declareProtected(View, 'getBibFolder')
    def getBibFolder(self):
	""" return the bibref items bibliography folder """
	return self.aq_inner.aq_parent	    
	    
    security.declareProtected(View, 'getSiteMembers')
    def getSiteMembers(self, *args, **kw):
        """
        For use when members are authors, return a DisplayList of members
        Alternative to 'getMembers' if 'no reference' must not be empty
        (to work around a bug in the 'Records' packager)
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        value = DisplayList()
        value.add('None', 'Select or specify')
        if self.showMemberAuthors() and not bib_tool.usesCMFMember():
            membertypes = bib_tool.getMemberTypes()
            sort_on = bib_tool.getSortMembersOn()
            select_attr_name = bib_tool.getSelectMembersAttr()
            catalog = getToolByName(self, 'portal_catalog')
            results = catalog(portal_type=membertypes,
                              sort_on=sort_on)
            for r in results:
                
                member_object = r.getObject()
                
                # if found object is translatable (LinguaPlone) make sure to use the canonical
                if member_object.isTranslatable():
                    member_object = member_object.getCanonical()
                
                # strip UID and selector field name from the found object
                uid = member_object.UID()
                select_attr = eval('member_object.%s' % select_attr_name) or None
                if callable(select_attr):
                    title = select_attr() or member_object.Title() or member_object.getId()
                else:
                    title = select_attr or member_object.Title() or member_object.getId()
                
                # add to value list for the member reference selector field in the authors widget    
                value.add(uid, title)
                
        elif self.showMemberAuthors() and bib_tool.usesCMFMember():   # BBB
            md = getToolByName(self, 'portal_memberdata')
            membertypes = md.getAllowedMemberTypes()
            catalog = getToolByName(self, 'portal_catalog')
            results = catalog(portal_type=membertypes,
                              sort_on='getId')
            for r in results:
                uid = getattr(aq_base(r), 'UID', r.getObject().UID())
                title = r.Title or r.getId
                value.add(uid, title)
                
        return value

    security.declareProtected(View, 'showMemberAuthors')
    def showMemberAuthors(self):
	""" return True if referencing of authors / editors to portal members is supported
	""" 
        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.getProperty('support_member_references')

    security.declareProtected(ModifyPortalContent, 'setMemberPublicationAuthors')
    def setMemberPublicationAuthors(self, value, **kw):
        """Default Mutator."""
        if kw.has_key('schema'):
            schema = kw['schema']
        else:
            schema = self.Schema()
            kw['schema'] = schema
        schema['member_publication_authors'].set(self, value, **kw)

    # support inline citations
    security.declareProtected(View, 'citationLabel')    
    def citationLabel(self, join_two='and', et_al='et al.'):
        """
        a short label for inline citations like
        "Ritz, 1995" or "Ritz and Herz, 2004" or
        "Ritz et al., 2005"
        """
        authors = self.getAuthorList()
        nofa = len(authors)
        year = self.getField('publication_year').get(self)

        if nofa == 0:
            return "Anonymous, %s" % year

        if nofa == 1:
            return "%s, %s" % (authors[0].get('lastname', ''),
                               year)        
        if nofa == 2:
            return "%s %s %s, %s" % (authors[0].get('lastname', ''),
                                     join_two,
                                     authors[1].get('lastname', ''),
                                     year)
        return "%s %s, %s" % (authors[0].get('lastname', ''),
                              et_al,
                              year) 

    security.declareProtected(View, 'getReference_type')    
    def getReference_type(self):
        return self.meta_type

    security.declareProtected(View, 'additionalReferenceInfo')    
    def additionalReferenceInfo(self):
        """
        'Authors (year): Source'
        to be shown in reference browser widgets
        """
        s = "%s (%s): %s" % (self.Authors(),
                             self.getPublication_year(),
                             self.Source()
                             )
        return s
