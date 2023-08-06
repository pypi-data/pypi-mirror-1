__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from DateTime import DateTime
import transaction
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import *
from Products.Archetypes.interfaces import IBaseContent
from Products.plonehrm.interfaces import IEmployeeModule
from plonehrm.jobperformance import config
from plonehrm.jobperformance.interfaces import IJobPerformanceInterview

from plonehrm.jobperformance import JobMessageFactory as _

schema = Schema((
    StringField(
        name='template',
        widget=SelectionWidget(
            format='select',
            condition='not:object/template_chosen',
            label=_(u'template', default=u'Template'),
        ),
        required=1,
        vocabulary='_templates'
    ),
    DateTimeField(
        name='date',
        default_method=DateTime,
        widget=CalendarWidget(
            label=_(u'label_date', default=u'Date'),
        )
    ),
    TextField('text',
              required=False,
              seachable=False,
              primary=True,
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = '',
                        label = _(u'label_body_text', default=u'Body Text'),
                        rows = 25,
                        condition='object/template_chosen'),
    ),
    LinesField(
        name='improvementAreas',
        widget=LinesWidget(
            condition='object/template_chosen',
            label=_(u'label_improvementAreas', default=u'Improvement areas'),
        )
    ),
),
)

Interview_schema = BaseSchema.copy() + schema.copy()


class JobPerformanceInterview(BaseContent):
    """
    """
    __implements__ = (BaseContent.__implements__, )
    implements(IEmployeeModule, IBaseContent, IJobPerformanceInterview)
    _at_rename_after_creation = True
    schema = Interview_schema

    # plonehrm.absence wants to know what the main date is:
    main_date = ATDateTimeFieldProperty('date')

    def _templates(self):
        """
        """
        jobtool = getToolByName(self, 'portal_jobperformance', None)
        if jobtool is None:
            return []
        else:
            items = [(item.id, item.Title())
                     for item in jobtool.contentValues()]
            return DisplayList(items)

    def initializeArchetype(self, **kwargs):
        """Pre-populate the jobperformance interview.

        Frankly, we would want a separate add form here, instead of an
        edit form that is also used for adding.
        """
        BaseContent.initializeArchetype(self, **kwargs)
        # Do not make the text required.
        self.schema['text'].required = False
        transaction.savepoint(optimistic=True)

    def setTemplate(self, value):
        jobtool = getToolByName(self, 'portal_jobperformance', None)
        if jobtool is None or value not in jobtool.contentIds():
            # Hm, odd.
            return
        self.template = value

        # Get the text from the template
        template_text = jobtool[self.template].getText()
        # Substitute parameters
        view = self.restrictedTraverse('@@substituter')
        template_text = view.substitute(template_text)
        self.setText(template_text)

        # Now we can make text required again
        self.schema['text'].required = True

    def template_chosen(self):
        """Determine if the template (a string) has been chosen yet.
        """
        return len(self.template) > 0


registerType(JobPerformanceInterview, config.PROJECTNAME)
