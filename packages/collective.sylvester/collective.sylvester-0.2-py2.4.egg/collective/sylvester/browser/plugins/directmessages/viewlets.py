from time import time
from twitter import Status
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import memoize
from Products.CMFPlone import PloneMessageFactory as _
from collective.sylvester.utils import cache_key_60, cache_key_3600

class DirectMessages(BrowserView):

    implements(IViewlet)
  
    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
        self.dashboard = self.context.restrictedTraverse('@@collective.sylvester.dashboard')

    def update(self):
        pass

    def name(self):
        return self.__name__

    def title(self):
        return _("Direct Messages")

    @memoize.ram.cache(cache_key_60)
    def _GetDirectMessages(self, username):
        """
        Cacheable companion to GetDirectMessages
        """
        return self.dashboard.twitter.GetDirectMessages()

    def GetDirectMessages(self):
        return self._GetDirectMessages(username=self.dashboard.twitter.username)

    # This can really be cached forever but due to RAM constraints it is 
    # sensible to limit the duration.
    @memoize.ram.cache(cache_key_3600)
    def message2status(self, message):
        """
        Convert message into a status

        xxx: this is a very limited conversion!
        """
        user = self.dashboard.twitter.GetUser(message.sender_id)
        status = Status(text=message.text, 
            created_at=message.created_at,
            user=user)
        return status

    def keepfresh(self):
        """
        We must always be ready with the answer
        """     
        self.GetDirectMessages()

    render = ViewPageTemplateFile("directmessages.pt")    
