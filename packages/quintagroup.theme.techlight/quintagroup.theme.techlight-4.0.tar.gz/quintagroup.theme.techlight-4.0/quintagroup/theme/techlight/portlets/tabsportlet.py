from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view

from quintagroup.theme.techlight import techlightMessageFactory as _

class ITabsPortlet(IPortletDataProvider):
    """A portlet.
    """

class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(ITabsPortlet)
    
    title = _(u'Tabs portlet')

class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('tabsportlet.pt')

    @property
    def portal_tabs(self):
        """Portal tabs"""
        return self.cachedTabs()

    @view.memoize
    def cachedTabs(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        portal_tabs_view = getMultiAdapter((self.context, self.context.REQUEST), name='portal_tabs_view')
        tabs = portal_tabs_view.topLevelTabs(actions=context_state.actions())
        return tabs

class AddForm(base.NullAddForm):
    
    def create(self):
        return Assignment()
