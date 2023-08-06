__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import logging

from zope.i18nmessageid import MessageFactory
from Products.Archetypes import atapi
from Products.CMFCore import permissions as cmfperms
from Products.CMFCore import utils as cmfutils

from plonehrm.checklist import config

ChecklistMessageFactory = MessageFactory(u'checklist')
logger = logging.getLogger('plonehrm.checklist')
logger.debug('Installing Product')


def initialize(context):
    import plonehrm.checklist.content

    # Initialize portal content
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types = content_types,
        permission = cmfperms.AddPortalContent,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)
