from Products.Five import BrowserView
from collective.habla.interfaces import IHablaChat
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

class HablaEnableChat(BrowserView):
    def __call__(self):
        alsoProvides(self.context, IHablaChat)
        self.request.response.redirect(self.context.absolute_url())

class HablaDisableChat(BrowserView):
    def __call__(self):
        noLongerProvides(self.context, IHablaChat)
        self.request.response.redirect(self.context.absolute_url())


class HablaChatEnabled(BrowserView):
    @property
    def is_chat_enabled(self):
        return IHablaChat.providedBy(self.context)
