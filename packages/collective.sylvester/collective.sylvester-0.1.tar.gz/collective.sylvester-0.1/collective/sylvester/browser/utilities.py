import twitter

from zope.interface import implements

from interfaces import ITwitterAPI

def wrapper(func_name, username, password, *args, **kwargs):
    api = twitter.Api(username, password)
    func = getattr(api, func_name)
    return func(*args, **kwargs)
 
class TwitterAPI(object):
    """
    Abstract python-twitter API. This class effectively modifies
    every callable method signature in python-twitter to expect
    username and password as parameters.
    """
    implements(ITwitterAPI)
  
    # List to lazily build a set of callable functions in
    # python-twitter
    __callable_functions__ = []
    
    def __getattr__(self, name):
        if hasattr(twitter.Api, name):           
            attr = getattr(twitter.Api, name)
            if callable(attr):
                if name not in self.__callable_functions__:
                    self.__callable_functions__.append(name)
                return lambda username, password, *args, **kwargs: wrapper(name, username, password, *args, **kwargs)
            else:
                return attr
        return getattr(object, name)
