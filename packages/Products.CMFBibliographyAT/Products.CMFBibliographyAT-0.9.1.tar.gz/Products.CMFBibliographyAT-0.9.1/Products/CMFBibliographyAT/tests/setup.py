from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# Make sure the dummy types are registered
from Products.CMFBibliographyAT.tests import dummy


ZopeTestCase.installProduct('CMFBibliographyAT')
PRODUCTS = ['CMFBibliographyAT',]
PloneTestCase.setupPloneSite(products=PRODUCTS)


# This is so we can find our own files
from Products.CMFBibliographyAT.tests import GLOBALS
from Globals import package_home
PACKAGE_HOME = package_home(GLOBALS)

from os.path import join
MEDLINE_TEST_MED = join(PACKAGE_HOME, 'medline_test.med')
MEDLINE_TEST_BIB = join(PACKAGE_HOME, 'medline_test.bib')
MEDLINE_TEST_XML = join(PACKAGE_HOME, 'medline_test.xml')
BIBTEX_TEST_BIB = join(PACKAGE_HOME, 'bibtex_test.bib')
IDCOOKING_TEST_BIB = join(PACKAGE_HOME, 'idcooking_test.bib')
PDFFOLDER_TEST_BIB = join(PACKAGE_HOME, 'pdffolder_test.bib')
CMFBAT_TEST_PDF_1 = join(PACKAGE_HOME, 'cmfbat-pdffile1.pdf')
CMFBAT_TEST_PDF_2 = join(PACKAGE_HOME, 'cmfbat-pdffile2.pdf')
CMFBAT_TEST_PDF_3 = join(PACKAGE_HOME, 'cmfbat-pdffile3.pdf')
BIBTEX_TEST_BIB_DUP = join(PACKAGE_HOME, 'bibtex_test_duplicates.bib')
BIBTEX_TEST_MULTI_AUTHORS = join(PACKAGE_HOME,
                                 'bibtex_test_multiauthors.bib')
BIBTEX_TEST_INBOOKREFERENCES = join(PACKAGE_HOME,
                                 'bibtex_test_inbookreferences.bib')
BIBTEX_TEST_LASTFIELDKOMMA = join(PACKAGE_HOME,
                                 'bibtex_test_lastfieldkomma.bib')
BIBTEX_TEST_TYPEFIELD = join(PACKAGE_HOME,
                                 'bibtex_test_typefield.bib')
BIBTEX_TEST_CITE_KEY = join(PACKAGE_HOME,
                            'bibtex_test_cite_key.bib')
CITATION_MANAGER_SOURCE = join(PACKAGE_HOME, 'citationmanager_test.txt')
RIS_SOURCE = join(PACKAGE_HOME, 'ris_test.ris')
