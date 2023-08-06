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

class TestBibliographyTool(PloneTestCase.PloneTestCase):
    '''Test the reference types'''

    def afterSetUp(self):
        pass

    # some utility methods

    def getEmptyBibFolder(self):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = 'bib_folder')
        return getattr(uf, 'bib_folder')

    def getPopulatedBibFolder(self):
        bf = self.getEmptyBibFolder()
        med_source = open('medline_test.med', 'r').read()
        bf.processImport(med_source, 'medline_test.med')
        return bf   

    # the individual tests

    def testGetReferenceTypes(self):
        bibtool = self.portal.portal_bibliography
        ref_types = list(bibtool.getReferenceTypes())
        ref_types.sort()
        # the expected types
        from Products.CMFBibliographyAT.config import REFERENCE_TYPES
        expected_types = list(REFERENCE_TYPES)
        expected_types.sort()
        self.assertEqual(ref_types, expected_types)

    def testImportFormats(self):
        bibtool = self.portal.portal_bibliography
        expected_names = ['BibTeX', 'Medline']
        names = bibtool.getImportFormatNames()
        # This makes sure we only check for the required types
        # IBSS, ISBN, PyBl might be present aswell
        names = [name for name in expected_names if name in names]
        names.sort()
        self.assertEqual(names, expected_names)
        expected_extensions = ['bib', 'med']
        extensions = bibtool.getImportFormatExtensions()
        # Filter, same as for names
        extensions = [ext for ext in expected_extensions if ext in extensions]
        extensions.sort()
        self.assertEqual(extensions, expected_extensions)

    def testExportFormats(self):
        bibtool = self.portal.portal_bibliography
        names = bibtool.getExportFormatNames()
        names.sort()
        expected_names = ['BibTeX', 'EndNote', 'PDF', 'RIS', 'XML (MODS)']
        extensions = bibtool.getExportFormatExtensions()
        extensions.sort()
        expected_extensions = ['bib', 'end', 'pdf', 'ris', 'xml']
        self.assertEqual(names, expected_names)
        self.assertEqual(extensions, expected_extensions)

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibliographyTool))
    return suite

if __name__ == '__main__':
    framework()
