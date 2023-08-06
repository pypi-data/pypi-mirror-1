from Acquisition import aq_inner
from collective.sylvester.browser.kssviews import BaseSylvesterKssView, \
    kssactionplus

class FollowingKssView(BaseSylvesterKssView):

    @kssactionplus
    def refreshFollowing(self, user_ids=None): 
        """
        Refresh a a few friendlets.
        """
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')

        view = context.restrictedTraverse('@@collective.sylvester.dashboard')
        mapping = view.GetUsersStatuses(user_ids=user_ids)
        for di in mapping.items():
            user = di['user']
            statuses = ['statuses']
            html = self.viewletMacroContent(                    
                    'collective.sylvester.friendletmanager', 
                    'collective.sylvester.friendlet', 
                    'main',
                    friend=user,
                    statuses=statuses)
            selector = ksscore.getHtmlIdSelector(
                'collective-sylvester-friendlet-friend%s' % user_id) 
            ksscore.replaceHTML(selector, html)
