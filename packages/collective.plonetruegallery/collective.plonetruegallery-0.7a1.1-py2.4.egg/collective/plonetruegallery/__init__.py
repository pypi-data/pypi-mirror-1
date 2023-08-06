__author__ = """Nathan Van Gheem"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('collective.plonetruegallery')
logger.debug('Installing Product')

import os
import os.path
from Globals import package_home
import Products.CMFPlone.interfaces
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.Archetypes.utils import capitalize
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit
from config import *
from Products.CMFCore.DirectoryView import registerDirectory

def initialize(context):
    """initialize product (called by zope)"""

    import galleryadapters
    import content

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)