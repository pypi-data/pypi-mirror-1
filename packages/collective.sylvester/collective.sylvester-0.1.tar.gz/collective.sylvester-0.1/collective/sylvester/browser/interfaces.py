from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

class ITwitterAPI(Interface):
    """
    Interface for python-twitter API
    """

class ITwitterCredentialsProvider(Interface):
    """
    Interface for adapter which provides twitter credentials
    """
   
    def username():
        """
        Return twitter username
        """

    def password():
        """
        Return twitter password
        """

class ISylvesterView(Interface):
    """
    Interface
    """

    def authenticate(redirect=False):
        """
        Call redirect_to_credentials_form if _setup_twitter_adapter returns 
        False.
        """

    def redirect_to_credentials_form():
        """
        Redirect to page where user can enter credentials for this session.
        """

    def _setup_twitter_adapter():      
        """
        Set up attribute on the view which carries authentication information.
        Return True if member can authenticate to twitter, False otherwise
        """

    def linkify(text):
        """
        Replace occurences of URI's in text with proper markup. Return the
        transformed text.
        """

    def format_ago(atime, uppercase=False, invert=False):
        """        
        Return a relative translated time string, eg. "4 hours ago" or
        "10 minutes ago".

        This method takes into account that the Zope server and the browser 
        may be in different timezones.

        atime: a parsable date string
        """

    def latest():
        """
        Return the latest status update by the authenticated member
        """

class ICredentialsFormView(Interface):
    """
    Interface
    """

    def name():
        """
        Return name that browser view is registered with in ZCML
        """

    def submit(username, password, came_from=''):
        """
        Handle form submission
        """

class IPublishToTwitterFormView(Interface):
    """
    Interface
    """

    def name():
        """
        Return name that browser view is registered with in ZCML
        """

    def submit(came_from=''):
        """
        Handle form submission
        """

class ISylvesterFriendletManager(IViewletManager):
    """ 
    Render a friend
    """

class ISylvesterStatusletManager(IViewletManager):
    """ 
    Render a status
    """
