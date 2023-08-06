from time import time
import re
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError
from twitter import TwitterError
try:
    from stripogram import html2text
    HAS_STRIPOGRAM = True
except ImportError:
    HAS_STRIPOGRAM = False
from DateTime import DateTime
from zope.interface import implements
from zope.component import getUtility, getAdapter
from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from plone import memoize

from interfaces import ISylvesterView, ICredentialsFormView, \
    IPublishToTwitterFormView, ITwitterAPI, ITwitterCredentialsProvider

TEXT_URL_TO_ANCHOR = re.compile(r'(((f|ht){1}tp://)[-a-zA-Z0-9@:%_\+.~#?&//=]+)', re.I|re.M)

# Handy decorator to catch exceptions and present useful
# error messages
def errorhandler(func):

    def new(self, *args, **kwargs):        
        # If handle_error is False then this decorator must let exceptions
        # propagate.
        handle_error = kwargs.get('handle_error', True)
        if not handle_error:
            return func(self, *args)

        viewname = ''
        try:
            return func(self, *args)
        except TwitterError:
            viewname = '@@collective.sylvester.service-error'
        except URLError:
            viewname = '@@collective.sylvester.service-error'
        except HTTPError, e:
            if e.msg == 'Unauthorized':
                viewname = '@@collective.sylvester.auth-error'
            else:
                viewname = '@@collective.sylvester.unknown-error'
        except:
            viewname = '@@collective.sylvester.unknown-error'

        context = aq_inner(self.context)
        self.request.RESPONSE.redirect('%s/%s' % (context.absolute_url(), viewname))

    return new

class TwitterAPIAdapter(object):
    """
    Utilities are unique in-memory objects which means we
    cannot store authentication information on them. We 
    need this adapter to provide authentication information 
    to the TwitterAPI utility.
    """

    def __init__(self, context, username, password):
        self.context = context
        self.username = username
        self.password = password

    def wrapper(self, func_name, *args, **kwargs):
        #import logging
        #logger = logging.getLogger('sylvester')
        #logger.info("doing a call to twitter %s" % func_name)
        func = getattr(self.context, func_name)
        # handle_error must be removed from kwargs since it is not known
        # to python-twitter.
        kw = kwargs.copy()
        if kw.has_key('handle_error'):
            del kw['handle_error']
        return func(self.username, self.password, *args, **kw)

    def __getattr__(self, name):           
        if hasattr(self.context, name):
            if name in self.context.__callable_functions__:
                return lambda *args, **kwargs: self.wrapper(name, *args, **kwargs)
            else:
                return getattr(self.context, name)
        return getattr(object, name)

class SylvesterView(BrowserView):

    implements(ISylvesterView)

    twitter = None

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._setup_twitter_adapter()

    def name(self):
        return self.__name__

    def authenticate(self, redirect=False):
        res = self._setup_twitter_adapter()
        if not res and redirect:
            self.redirect_to_credentials_form()
        return res

    def redirect_to_credentials_form(self):
        #Redirect to page where user can enter credentials for this session.
        portal = getToolByName(self, 'portal_url').getPortalObject()
        self.request.response.redirect(
                '%s/@@collective.sylvester.credentials-form?came_from=%s' \
                % (portal.absolute_url(), url_quote(self.request.URL)))

    def _setup_twitter_adapter(self):      
        username, password = 'unlikely', 'u;n;l;i;k;e;l;y'
        # Check if the session is storing credentials
        session = self.request.SESSION
        if session.has_key('collective.sylvester.twitter'):
            username = session['collective.sylvester.twitter']['username']
            password = session['collective.sylvester.twitter']['password']                
        else:
            # Find an adapter which can retrieve twitter credentials for the 
            # authenticated member.
            pms = getToolByName(self.context, 'portal_membership')
            if not pms.isAnonymousUser(): 
                member = pms.getAuthenticatedMember()
                adapter = getAdapter(member, ITwitterCredentialsProvider)
                if adapter is not None:            
                    username, password = adapter.username(), adapter.password()

        # Return false if username lookup failed
        if (username == 'unlikely') and (password == 'u;n;l;i;k;e;l;y'):
            return False

        # Setup twitter attribute
        self.twitter = TwitterAPIAdapter(
                            getUtility(ITwitterAPI),
                            username, password)

        # Test authentication. GetFriends is the lightest method I could find
        # for this use-case and this class will cache the result on the request.
        try:
            self.GetFriends(user=None)
        except HTTPError, e:
            # Catch only unauthorized
            if e.msg == 'Unauthorized':
                return False            
            raise

        return True

    def linkify(self, text):
        return TEXT_URL_TO_ANCHOR.sub('<a href="\g<1>">\g<1></a>', text)
    
    def format_ago(self, atime, uppercase=False, invert=False):                
        try:
            dt = DateTime(atime)
        except ValueError:
            return None

        now = DateTime().toZone('GMT+0')
        now_secs = float(now)
        dt_secs = float(dt) 

        if not invert:
            # This case is for 'X time ago'. If smaller than zero just set to 
            # zero.
            diff = now_secs - dt_secs    
            if diff < 0:
                diff = 0
        else:
            # This case is for 'X time left'. If smaller than zero then no time 
            # left, so return None.
            diff = dt_secs - now_secs
            if diff <= 0:
                return None

        ret = ''
        if diff < 3600:
            minutes = int(diff / 60)
            if minutes == 1:
                ret = _('1 minute')
            else:
                ret = _('%s minutes' % minutes)
        elif (diff >= 3600) and (diff < 86400):
            hours = int(diff / 3600)
            if hours == 1:
                ret = _('1 hour')
            else:
                ret = _('%s hours' % hours)
        elif diff >= 86400:
            days = int(diff / 86400)
            if days == 1:
                ret = _('1 day')
            else:
                ret = _('%s days' % days)

        if uppercase:
            return ret.upper()

        return ret

    def latest(self):
        result = self.twitter.GetUserTimeline(count=1)
        if result:
            return result[0]
        return None

    @memoize.ram.cache(lambda *args: time() // 60)
    def GetFriendsTimeline(self, user=None, since=None):
        """
        This call is potentially too slow for normal use in ajax requests.
        The dashboard makes this call when it is first loaded, which provides
        an opportunity to use a memoize decorator.
        """
        return self.twitter.GetFriendsTimeline(user=user, since=since)

    @memoize.ram.cache(lambda *args: time() // 60)
    def GetReplies(self):
        """
        Cached for the same reason as GetFriendsTimeline
        """
        return self.twitter.GetReplies()

    def GetFriendsStatuses(self, user_ids=None):
        """
        Take the result from GetFriendsTimeline and group the statuses by user.
        Return a list of dictionaries of the form 
        {'user':user, 'statuses':statuses}
        """
        user_status_map = {}
        userid_user_map = {}
        for status in self.GetFriendsTimeline():
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

    @memoize.request.cache(
        lambda func, obj, user: (func.func_name, user), 
        get_request='self.request')
    def GetFriends(self, user=None):
        return self.twitter.GetFriends(user=user)

    @errorhandler
    def __call__(self, *args, **kwargs):
        if not self.authenticate(redirect=True):
            return 

        # The template is cleaner if we disable the border here
        self.request.set('disable_border', 1)

        return super(SylvesterView, self).__call__(*args, **kwargs)

class CredentialsFormView(BrowserView):

    implements(ICredentialsFormView)

    def name(self):
        return self.__name__

    def submit(self, username, password, came_from=''):
        session = self.request.SESSION
        if not session.has_key('collective.sylvester.twitter'):
            session['collective.sylvester.twitter'] = {}
        session['collective.sylvester.twitter']['username'] = username
        session['collective.sylvester.twitter']['password'] = password

        getToolByName(self, 'plone_utils').addPortalMessage(
            _("Twitter credentials saved for this session"))
        if came_from:
            self.request.response.redirect(came_from)
        else:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            self.request.response.redirect(portal.absolute_url())

    def __call__(self, *args, **kwargs):
        form = self.request.form
        if form.has_key('submit'):
            return self.submit(
                form.get('username', ''), 
                form.get('password', ''),
                form.get('came_from', ''))

        self.request.set('disable_border', 1)
        return super(CredentialsFormView, self).__call__(*args, **kwargs)

class PublishToTwitterFormView(BrowserView):

    implements(IPublishToTwitterFormView)

    def name(self):
        return self.__name__

    @errorhandler
    def submit(self, came_from=''):
        # Build up a string from the Description field if it has a value.If 
        # it is empty then use a stripped Text field if present. If both yield 
        # an empty string then use only a tinyurl link.
        context = aq_inner(self.context)
        text = context.Description()
        if not text and HAS_STRIPOGRAM:
            if context.Schema().getField('text') is not None:
                text = html2text(context.getText())
                
        # Get a tiny url link
        url_data = urlencode(dict(url=context.absolute_url()))
        try:
            link = urlopen(
                'http://tinyurl.com/api-create.php', 
                data=url_data).read().strip()
        except URLError:
            msg = "An error was encountered while attempting to shorten the URL"
            getToolByName(self, 'plone_utils').addPortalMessage(_(msg), 'error')
            self.request.response.redirect(context.absolute_url())
            return

        # Reduce length of text
        text = text[:(137-len(link))]

        # Send to twitter
        view = context.restrictedTraverse('@@collective.sylvester.dashboard')
        message = '%s...%s' % (text, link)
        view.twitter.PostUpdate(message, handle_error=False)
        getToolByName(self, 'plone_utils').addPortalMessage(
            _("Item published to twitter"))
        self.request.response.redirect(context.absolute_url())

    def __call__(self, *args, **kwargs):
        form = self.request.form
        if form.has_key('submit'):
            return self.submit(
                form.get('came_from', ''))

        # Redirect if member cannot authenticate to twitter
        context = aq_inner(self.context)
        view = context.restrictedTraverse('@@collective.sylvester.dashboard')
        if not view.authenticate(redirect=True):
            return

        self.request.set('disable_border', 1)
        return super(PublishToTwitterFormView, self).__call__(*args, **kwargs)
