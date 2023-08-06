__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('plonehrm.personaldata')
logger.debug('Installing Product')

from zope.i18nmessageid import MessageFactory
PersonalMessageFactory = MessageFactory(u'personaldata')

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore import utils as cmfutils

from plonehrm.personaldata import config

def initialize(context):
    # imports packages and types for registration
    import content
    content # PYFLAKES

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = 'plonehrm: Add personaldata',
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
