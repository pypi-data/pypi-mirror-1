__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('jobperformance')
logger.debug('Installing Product')

from zope.i18nmessageid import MessageFactory
JobMessageFactory = MessageFactory(u'jobperformance')

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit
from plonehrm.jobperformance import config


def initialize(context):
    # imports packages and types for registration
    import content
    import tool
    content # PYFLAKES

    # Initialize portal tools
    tools = [tool.JobPerformanceTool]
    ToolInit(config.PROJECTNAME +' Tools',
             tools = tools,
             icon='tool.gif'
             ).initialize( context )

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = 'plonehrm: Add performance interview',
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
