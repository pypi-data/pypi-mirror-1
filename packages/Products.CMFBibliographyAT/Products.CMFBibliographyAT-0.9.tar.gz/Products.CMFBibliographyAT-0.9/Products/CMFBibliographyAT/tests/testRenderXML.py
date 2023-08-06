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


class TestRenderXML(PloneTestCase.PloneTestCase):
    """Test rendering to XML.
    """

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

    def testRenderXML(self):
        bf = self.getPopulatedBibFolder()
        xml_source = bf.bibliography_export(format='XML').strip()
        expected_source = open(setup.MEDLINE_TEST_XML, 'r').read().strip()
        # just in case we need to debug that again        
        #l1 = bib_source.splitlines(1)
        #l2 = expected_source.splitlines(1)
        #from difflib import Differ
        #from pprint import pprint
        #d = Differ()
        #pprint(list(d.compare(l1,l2)))
        self.assertEqual(xml_source, expected_source)

    # end of the individual tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRenderXML))
    return suite

if __name__ == '__main__':
    framework()
