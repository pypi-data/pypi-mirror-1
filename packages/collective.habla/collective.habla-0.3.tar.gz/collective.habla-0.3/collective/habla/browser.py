from collective.habla import HablaMessageFactory as _
from collective.habla.interfaces import IHablaChat
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

class HablaEnableChat(BrowserView):
    def __call__(self):
        alsoProvides(self.context, IHablaChat)
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(_("The chat has been enabled"))
        self.request.response.redirect(self.context.absolute_url())

class HablaDisableChat(BrowserView):
    def __call__(self):
        noLongerProvides(self.context, IHablaChat)
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(_("The chat has been disabled"))
        self.request.response.redirect(self.context.absolute_url())


class HablaChatEnabled(BrowserView):
    @property
    def is_chat_enabled(self):
        return IHablaChat.providedBy(self.context)
