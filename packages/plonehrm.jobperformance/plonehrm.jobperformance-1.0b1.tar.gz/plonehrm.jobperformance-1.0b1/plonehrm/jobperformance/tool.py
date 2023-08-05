__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
import config
from Products.CMFCore.utils import UniqueObject

jobperformance_schema = BaseFolderSchema.copy()

class JobPerformanceTool(UniqueObject, BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UniqueObject,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    id = 'portal_jobperformance'
    typeDescription = "Job performance templates"
    typeDescMsgId = 'description_edit_jobperformancetool'
    #toolicon = 'JobPerformance.gif'
    schema = jobperformance_schema

    # tool-constructors have no id argument, the id is fixed
    def __init__(self):
        self.id = 'portal_jobperformance'
        self.setTitle('Job Performance Templates')
        self.unindexObject()

    def at_post_edit_script(self):
        """ Because we inherit from BaseFolder and call setTitle our tool is being
        index against our will.
        """
        self.unindexObject()

registerType(JobPerformanceTool, config.PROJECTNAME)
