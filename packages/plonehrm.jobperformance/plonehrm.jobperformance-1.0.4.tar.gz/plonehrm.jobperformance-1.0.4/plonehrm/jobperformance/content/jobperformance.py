__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from DateTime import DateTime
import transaction
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IBaseContent
from Products.plonehrm.interfaces import IEmployeeModule
from plonehrm.jobperformance import config
from plonehrm.jobperformance.interfaces import IJobPerformanceInterview

from plonehrm.jobperformance import JobMessageFactory as _

schema = atapi.Schema((
    atapi.StringField(
        name='template',
        widget=atapi.SelectionWidget(
            format='select',
            condition='not:object/template_chosen',
            label=_(u'template', default=u'Template'),
            ),
        required=1,
        vocabulary='_templates'
        ),
    atapi.DateTimeField(
        name='date',
        default_method=DateTime,
        widget=atapi.CalendarWidget(
            label=_(u'label_date', default=u'Date'),
            )
        ),
    atapi.TextField(
        'text',
        required=False,
        seachable=False,
        primary=True,
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
            description = '',
            label = _(u'label_body_text', default=u'Body Text'),
            rows = 25,
            condition='object/template_chosen'
            ),
        ),
    atapi.LinesField(
        name='improvementAreas',
        widget=atapi.LinesWidget(
            condition='object/template_chosen',
            label=_(u'label_improvementAreas', default=u'Improvement areas'),
            )
        ),
    ))

Interview_schema = atapi.BaseSchema.copy() + schema.copy()


class JobPerformanceInterview(atapi.BaseContent):
    """
    """
    __implements__ = (atapi.BaseContent.__implements__, )
    implements(IEmployeeModule, IBaseContent, IJobPerformanceInterview)
    _at_rename_after_creation = True
    schema = Interview_schema

    # plonehrm.absence wants to know what the main date is:
    main_date = atapi.ATDateTimeFieldProperty('date')

    def _templates(self):
        """
        """
        jobtool = getToolByName(self, 'portal_jobperformance', None)
        if jobtool is None:
            return []
        else:
            items = [(item.id, item.Title())
                     for item in jobtool.listTemplates()]
            return atapi.DisplayList(items)

    def initializeArchetype(self, **kwargs):
        """Pre-populate the jobperformance interview.

        Frankly, we would want a separate add form here, instead of an
        edit form that is also used for adding.
        """
        atapi.BaseContent.initializeArchetype(self, **kwargs)
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


atapi.registerType(JobPerformanceInterview, config.PROJECTNAME)
