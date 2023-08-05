from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
import logging
logger = logging.getLogger('plonehrm')
# This is needed in Zope 2.9.7-8
# When moving to Plone 3 we can use Five's BrowserView
from Acquisition import Explicit
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from plonehrm.jobperformance import JobMessageFactory as _


class JobPerformanceView(Explicit):
    implements(IViewlet)
    render = ViewPageTemplateFile('jobperformance.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    @property
    def interviews(self):
        contentFilter = {'portal_type': 'JobPerformanceInterview'}
        brains = self.context.getFolderContents(contentFilter=contentFilter)
        objects = [brain.getObject() for brain in brains]
        items = [{'title': obj.Title(),
                  'url': obj.absolute_url(),
                  'date': obj.getDate()} for obj in objects]
        def date_key(item):
            return item['date']
        items.sort(key=date_key)
        items.reverse()
        return items[:3]

    @property
    def improvementAreas(self):
        contentFilter = {'portal_type': 'JobPerformanceInterview',
                         'sort_on': 'Date'}
        brains = self.context.getFolderContents(
            contentFilter=contentFilter)
        if not brains:
            return []
        brain = brains[-1]
        if brain:
            item = brain.getObject()
            return item.getImprovementAreas()
        else:
            return None


class SimpleJobPerformanceView(JobPerformanceView):
    """Simple viewlet for seeing a checklist."""
    implements(IViewlet)
    render = ViewPageTemplateFile('improvement_areas.pt')

    def header(self):
        return _('Improvement areas')


class ShowImprovementEditForm(PloneKSSView):
    """kss view for adding a note"""
    @kssaction
    def edit_improvement(self):
        """Show the edit template of improvementAreas"""
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('improvement-areas')
        view = self.context.restrictedTraverse('@@improvement_edit')
        rendered = view()
        core.replaceHTML(selector, rendered)
        core.focus('#improvementAreas')


class ShowImprovementView(PloneKSSView):
    """kss view for adding a note"""

    @kssaction
    def view_improvement(self, areas=False):
        """Save the improvementAreas"""
        if areas != False:
            self.context.setImprovementAreas(areas)
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('improvement-areas-edit')
        view = self.context.restrictedTraverse('@@improvement_view')
        rendered = view()
        core.replaceHTML(selector, rendered)
