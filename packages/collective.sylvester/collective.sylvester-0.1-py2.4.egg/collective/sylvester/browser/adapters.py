from zope.interface import implements
from interfaces import ITwitterCredentialsProvider

class MemberDataTwitterCredentialsProvider:

    implements(ITwitterCredentialsProvider)

    def __init__(self, context):
        self.context = context

    def username(self):
        return self.context.getProperty('twitterUsername')

    def password(self):
        return self.context.getProperty('twitterPassword')

class ReMemberTwitterCredentialsProvider:

    implements(ITwitterCredentialsProvider)

    def __init__(self, context):
        self.context = context

    # Do not use ClassGen accessors since they do not work if the fields
    # are provided by schema extension
    def username(self):
        return self.context.Schema().getField('twitterUsername').getAccessor(self.context)()

    def password(self):
        return self.context.Schema().getField('twitterPassword').getAccessor(self.context)()

