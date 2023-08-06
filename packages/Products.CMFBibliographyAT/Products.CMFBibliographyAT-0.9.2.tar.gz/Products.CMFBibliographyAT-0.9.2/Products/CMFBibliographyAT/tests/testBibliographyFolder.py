##################################################
#                                                #
#    Copyright (C), 2004, Raphael Ritz           #
#    <r.ritz@biologie.hu-berlin.de>              #
#                                                #
#    Humboldt University Berlin                  #
#                                                #
##################################################

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFBibliographyAT.tests import setup
from Products.CMFCore.utils import getToolByName


class TestBibliographyFolder(PloneTestCase.PloneTestCase):
    '''Test the BibliographyFolder'''

    def afterSetUp(self):
        self._refreshSkinData()

    # some utility methods

    def getEmptyBibFolder(self):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = 'bib_folder')
        return getattr(uf, 'bib_folder')

    def getPopulatedBibFolder(self, source_file=setup.MEDLINE_TEST_MED, format="med"):
        bf = self.getEmptyBibFolder()
        source = open(source_file, 'r').read()
        bf.processImport(source, 'source.%s' % format)
        return bf

    # the individual tests

    def test_FolderCreation(self):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = 'test_folder')
        self.failUnless('test_folder' in uf.contentIds())

    def test_MedlineImport(self):
        bf = self.getEmptyBibFolder()
        med_source = open(setup.MEDLINE_TEST_MED, 'r').read()
        bf.processImport(med_source, 'medline_test.med')
        expected_ids = ['GrootEtAl2003',
                        'AlibardiThompson2003',
                        'CokeEtAl2003',
                        'TrapeMane2002']
        for id in expected_ids:
            self.failUnless(id in bf.contentIds(),
                            'Importing %s failed.' % id)

    def test_BibtexImport(self):
        bf = self.getEmptyBibFolder()
        bib_source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        bf.processImport(bib_source, 'bibtex_test.bib')
        expected_ids = ['Lutz2001',
                        'Lattier2001',
                        'McKay2003']
        for id in expected_ids:
            self.failUnless(id in bf.contentIds(),
                            'Importing %s failed.' % id)
        # Test the annote handling
        self.failUnless(bf['McKay2003'].getAnnote() == 'I really like it.')

    def test_BibtexExport(self):
        bf = self.getPopulatedBibFolder()
        bib_source = bf.bibliography_export(format='BibTeX').strip()
        expected_source = open(setup.MEDLINE_TEST_BIB, 'r').read().strip()
        # just in case we need to debug that again        
        #l1 = bib_source.splitlines(1)
        #l2 = expected_source.splitlines(1)
        #from difflib import Differ
        #from pprint import pprint
        #d = Differ()
        #pprint(list(d.compare(l1,l2)))
        self.assertEqual(bib_source, expected_source)

    def test_BibtexExportCiteKeys(self):
        bf = self.getPopulatedBibFolder(setup.BIBTEX_TEST_CITE_KEY, 'bib')
        bib_source = bf.bibliography_export(format='BibTeX').strip()
        #expected_source = open(setup.BIBTEX_TEST_CITE_KEY, 'r').read().strip()
        self.failUnless(bib_source.startswith('@Book{Esping-Andersen1985'))

    def test_BibtexExportIgnoresNonBibrefItems(self):
        bf = self.getPopulatedBibFolder()
        bf.getPdfFolder() # non-bibref item
        bib_source = bf.bibliography_export(format='BibTeX').strip()
        expected_source = open(setup.MEDLINE_TEST_BIB, 'r').read().strip()
        self.assertEqual(bib_source, expected_source)

    # for the folder defaults
    def test_AuthorURLs(self):
        bf = self.getEmptyBibFolder()
        link_list = [{'key':'foo',
                      'value':'foos_home'},
                     {'key':'bar',
                      'value':'bars_home'}]
        bf.processAuthorUrlList(link_list)
        self.assertEqual(bf.AuthorURLs()['foo'], 'foos_home')
        self.assertEqual(bf.AuthorURLs()['bar'], 'bars_home')

    def test_getPublicationsByAuthors(self):
        bf = self.getPopulatedBibFolder()
        # one author
        refs  = bf.getPublicationsByAuthors('J Trape')
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].getId(), 'TrapeMane2002')
        # joint authors (and_flag false)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'Y Mane'])
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].getId(), 'TrapeMane2002')
        # joint authors (and_flag true)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'Y Mane'],
                                            1)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].getId(), 'TrapeMane2002')
        # disjoint authors (and_flag false)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'T Groot'])
        ref_ids = [ref.getId() for ref in refs]
        self.assertEqual(len(refs), 2)
        self.failUnless('TrapeMane2002' in ref_ids)
        self.failUnless('GrootEtAl2003' in ref_ids)        
        # disjoint authors (and_flag true)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'T Groot'],
                                            1)
        self.assertEqual(len(refs), 0)

    def test_Top(self):
        bf = self.getPopulatedBibFolder()
        bf.setTop(['TrapeMane2002', 'GrootEtAl2003', 'CokeEtAl2003'])
        top_2 = [ref.getId() for ref in bf.Top(2)]
        self.assertEqual(top_2, ['TrapeMane2002', 'GrootEtAl2003'])

    def test_processImportReturnsObjects(self):
        bf = self.getEmptyBibFolder()
        med_source = open(setup.MEDLINE_TEST_MED, 'r').read()
        result = bf.processImport(med_source,
                                  'medline_test.med',
                                  return_obs=True,
                                  )
        self.assertEqual(len(result), 4)

    def test_cookId(self):
        bf = self.getEmptyBibFolder()
        ref_dict1 = {'authors' : [ {'lastname'  : 'Hicks',
                                    'firstname' : 'Tim',
                                    'middlename': 'M.',
                                    },
                                   {'lastname'  : 'Smith',
                                    'firstname' : 'Tom',
                                    'middlename': 'W.',
                                    },
                                 ],
                     'publication_year' : '2006'
                     }
        id1 = bf.cookId(ref_dict1)
        self.assertEqual(id1, 'HicksSmith2006')
        ref_dict2 = {'authors' : [ {'lastname'  : 'Hicks',
                                    'firstname' : 'Tim',
                                    'middlename': 'M.',
                                    },
                                   {'lastname'  : 'Smith',
                                    'firstname' : 'Tom',
                                    'middlename': 'W.',
                                    },
                                   {'lastname'  : 'Parsons',
                                    'firstname' : 'Tammy',
                                    'middlename': 'T.',
                                    },
                                 ],
                     'publication_year' : '2006'
                     }
        id2 = bf.cookId(ref_dict2)
        self.assertEqual(id2, 'HicksEtAl2006')

    def test_listDAVObjects(self):
        bf = self.getPopulatedBibFolder()
        # Get hold of a (random) reference object.
        an_obj = getattr(bf, 'GrootEtAl2003')
        # Check that listDAVObjects returns it.
        self.failUnless(an_obj in bf.listDAVObjects())
        # Transition the object to the 'private' state to limit access to it.
        wtool = getToolByName(bf, 'portal_workflow')
        wtool.doActionFor(an_obj, 'hide')
        # Give ourselves limited access
        self.logout()
        # Check that our newly-limited access stops us seeing the obj.
        self.failIf(an_obj in bf.listDAVObjects())

    # end of the individual tests


class TestLargeBibliographyFolder(TestBibliographyFolder):
    """Test the LargeBibliographyFolder.
    We subclass the TestBibliographyFolder test case so that all of those tests
    are applied to LargeBibliographyFolders as well.
    """

    def afterSetUp(self):
        self._refreshSkinData()
        # Make sure that 'LargeBibliographyFolder' is an addable type...
        ttool = getToolByName(self.folder, 'portal_types')
        ftype = getattr(ttool, 'Folder')
        ftype_allowed = list(ftype.getProperty('allowed_content_types'))
        ftype_allowed.append('LargeBibliographyFolder')
        ftype.manage_changeProperties(allowed_content_types=ftype_allowed)

    # some utility methods

    def getEmptyBibFolder(self):
        uf = self.folder
        uf.invokeFactory(type_name='LargeBibliographyFolder',
                         id='bib_folder')
        return getattr(uf, 'bib_folder')

    def getPopulatedBibFolder(self,
                              source_file=setup.MEDLINE_TEST_MED,
                              format='med'):
        bf = self.getEmptyBibFolder()
        source = open(source_file, 'r').read()
        bf.processImport(source, 'source.%s' % format)
        return bf

    # the individual tests


    # end individual tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibliographyFolder))
    suite.addTest(makeSuite(TestLargeBibliographyFolder))
    return suite

if __name__ == '__main__':
    framework()
