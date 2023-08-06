from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry
from zope.component import getUtility

class HablaViewlet(ViewletBase):
    index = ViewPageTemplateFile('habla_portlets.pt')

    @property
    def habla_id(self):
        settings = getUtility(IRegistry)
        return settings.records['collective.habla.habla_id'].value
