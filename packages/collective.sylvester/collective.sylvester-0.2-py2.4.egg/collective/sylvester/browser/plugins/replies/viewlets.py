from time import time
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import memoize
from Products.CMFPlone import PloneMessageFactory as _
from collective.sylvester.utils import cache_key_60

class Replies(BrowserView):

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
        if self.dashboard.twitter is not None:
            return "@%s" % self.dashboard.twitter.username
        return _("Mentions")

    @memoize.ram.cache(cache_key_60)
    def _GetReplies(self, username):
        """
        Cacheable companion to GetReplies
        """
        return self.dashboard.twitter.GetReplies()

    def GetReplies(self):
        return self._GetReplies(username=self.dashboard.twitter.username)

    def keepfresh(self):
        """
        We must always be ready with the answer
        """
        self.GetReplies()

    render = ViewPageTemplateFile("replies.pt")    
