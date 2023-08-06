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

class TestReferenceTypes(PloneTestCase.PloneTestCase):
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
        med_source = open(setup.MEDLINE_TEST_MED, 'r').read()
        bf.processImport(med_source, 'medline_test.med')
        return bf   

    # the individual tests

    def test_ArticleCreation(self):
        bf = self.getEmptyBibFolder()
        bf.invokeFactory(type_name = 'ArticleReference',
                         id = 'test_article')
        self.failUnless('test_article' in bf.contentIds())

    def test_ArticleSource(self):
        bf = self.getPopulatedBibFolder()
        source = bf.CokeEtAl2003.Source()
        expected_source = 'Am J Vet Res, 64(2):225-8.'
        self.assertEqual(source, expected_source)

    def test_getPdfFolder(self):
        bf = self.getPopulatedBibFolder()
        entry = bf.CokeEtAl2003
        o1 = bf.getPdfFolder()
        o2 = entry.getPdfFolder()
        self.assertEqual(o1, o2)
        self.failUnless('pdfs' in bf.contentIds())
        folder_type = o1.portal_type
        self.assertEqual(folder_type, 'PDF Folder')
        

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestReferenceTypes))
    return suite

if __name__ == '__main__':
    framework()
