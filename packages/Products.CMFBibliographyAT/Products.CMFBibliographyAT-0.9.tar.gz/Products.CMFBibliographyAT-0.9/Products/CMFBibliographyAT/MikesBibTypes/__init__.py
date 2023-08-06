from Globals import package_home
from Products.Archetypes.public import *
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

from config import *

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    ##Import Types here to register them
    import BibFolder
    import Book
    import Article
    import Chapter
    import Journal
    import TechnicalReport
    import Thesis
    import Proceedings
    import ConferencePaper
    import NewsArticle
    import Standard

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

