__author__ = """Nathan Van Gheem"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('collective.plonetruegallery')
logger.debug('Installing Product')

from zope.i18nmessageid import MessageFactory
PTGMessageFactory = MessageFactory("collective.plonetruegallery")

import validators

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.CMFCore import utils as cmfutils

def initialize(context):
    """initialize product (called by zope)"""

    from content import gallery

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes('collective.plonetruegallery'), 'collective.plonetruegallery')

    cmfutils.ContentInit(
        'collective.plonetruegallery Content',
        content_types      = all_content_types,
        permission         = 'collective.plonetruegallery: manage galleries',
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)