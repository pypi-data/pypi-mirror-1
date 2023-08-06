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

class TestContentTypes(PloneTestCase.PloneTestCase):
    '''Test the various content types'''

    def afterSetUp(self):
        self._refreshSkinData()

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

    def test_plainTextAbstract(self):
        bf = self.getPopulatedBibFolder()
        article = getattr(bf, 'GrootEtAl2003')
        abstract = "\nMy special abstract\n"
        article.setAbstract(abstract, mimetype='text/plain')
        self.assertEqual(str(article.editAbstract()), abstract)

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentTypes))
    return suite

if __name__ == '__main__':
    framework()
