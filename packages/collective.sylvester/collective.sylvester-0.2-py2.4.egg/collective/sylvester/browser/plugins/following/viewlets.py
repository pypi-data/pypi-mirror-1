from time import time
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import memoize
from Products.CMFPlone import PloneMessageFactory as _

class Following(BrowserView):

    implements(IViewlet)
  
    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager

    def update(self):
        pass

    def name(self):
        return self.__name__

    def title(self):
        return _("Following")

    def GetFollowingStatuses(self, user_ids=None):
        """
        Take the result from GetFriendsTimeline and group the statuses by user.
        Return a list of dictionaries of the form 
        {'user':user, 'statuses':statuses}
        """
        view = self.context.restrictedTraverse('@@collective.sylvester.dashboard')
        user_status_map = {}
        userid_user_map = {}
        for status in view.GetFriendsTimeline():
            # Skip over users we are not interested in
            if (user_ids is not None) and (status.user.id not in user_ids):
                continue
            user_status_map.setdefault(status.user.id, [])
            user_status_map[status.user.id].append(status)
            userid_user_map[status.user.id] = status.user
        
        result = []
        for userid, statuses in user_status_map.items():
            result.append(dict(user=userid_user_map[userid], statuses=statuses))

        # Sort
        def mysort(a, b):
            return cmp(a['user'].screen_name, b['user'].screen_name)
        result.sort(mysort)

        return result

    render = ViewPageTemplateFile("following.pt")    
