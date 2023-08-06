import types
from urllib2 import HTTPError, URLError
from twitter import TwitterError

from Acquisition import aq_inner, aq_parent
from Acquisition import Implicit
from zope.interface import implements
from zope.component import getAdapters, queryMultiAdapter, getUtility
from zope.viewlet.interfaces import IViewletManager, IViewlet
from kss.core import kssaction, force_unicode
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from interfaces import ITwitterAPI

# We cannot use a normal decorator since there are issues with marshalling.
# Luckily kss.core provides the kssaction decorator which we can subclass
# in a creative way. It is easier than attempting to chain decorators.
class kssactionplus(kssaction):

    def apply(self, obj, *arg, **kw):
        try:
            # Clear our own error messages
            ksscore = obj.getCommandSet('core')
            selector = ksscore.getHtmlIdSelector('collective-sylvester-dashboard-messages')
            ksscore.replaceInnerHTML(selector, '')
            
            # Clear Plone's messages
            kssplone = obj.getCommandSet('plone')
            kssplone.issuePortalMessage('')

            return kssaction.apply(self, obj, *arg, **kw)

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
       
        html = obj.macroContent('%s/macros/main' % viewname)        
        kssplone = obj.getCommandSet('plone')
        kssplone.issuePortalMessage(html, msgtype='error')
        return obj.render()

class BaseSylvesterKssView(Implicit, PloneKSSView):
    """
    Methods _macroContent, viewletMacroContent, macrocontent from 
    https://svn.plone.org/svn/plone/plone.app.kss/branches/hedley-macrocontent
    included. I omit the docstrings.
    """

    implements(IPloneKSSView)

    def _macroContent(self, provider, macro_name, context=None, **kw):
        # Determine context to use for rendering
        if context is None:
            render_context = aq_inner(self.context)
        else:
            render_context = context

        # Build extra context. These variables will be in
        # scope for the macro.        
        extra_context = {'options':{}}
        extra_context.update(kw)
        the_macro = None

        # Determine what type of provider we are dealing with
        if isinstance(provider, types.StringType):
            # Page template or browser view. Traversal required.
            pt_or_view = render_context.restrictedTraverse(provider)
            if provider.startswith('@@'):            
                the_macro = pt_or_view.index.macros[macro_name]
            else:          
                the_macro = pt_or_view.macros[macro_name]

            # template_id seems to be needed, so add to options
            # if it is not there
            if not extra_context['options'].has_key('template_id'):
                extra_context['options']['template_id'] = provider.split('/')[-1]

        elif IViewlet.isImplementedBy(provider) or IPortletRenderer.isImplementedBy(provider):
            the_macro = provider.render.macros[macro_name]
        
        # Adhere to header_macros convention. Setting the_macro here
        # ensures that code calling this method cannot override the_macro.
        extra_context['options']['the_macro'] = the_macro

        # If context is explicitly passed in then make available        
        if context is not None:
            extra_context['context'] = context

        if hasattr(self, 'header_macros'):
            # plone.app.kss <= 1.4.3
            content = self.header_macros.__of__(render_context).pt_render(
                        extra_context=extra_context)
        else:
            # plone.app.kss > 1.4.3
            from plone.app.kss.plonekssview import header_macros
            content = header_macros.__of__(self).__of__(render_context).pt_render(
                        extra_context=extra_context)

        # IE6 has problems with whitespace at the beginning of content
        content = content.strip()

        # Always encoded as utf-8
        content = force_unicode(content, 'utf')
        return content

    def viewletMacroContent(self, manager_name, viewlet_name, macro_name, 
        context=None, **kw):
        manager = queryMultiAdapter(
            (self.context, self.request, self), 
            IViewletManager, 
            name=manager_name)

        viewlets = getAdapters(
            (manager.context, manager.request, manager.__parent__, manager), 
            IViewlet)

        target = None
        for order, (name, viewlet) in enumerate(viewlets):
            if name == viewlet_name:               
                return self._macroContent(viewlet, macro_name, context, view=viewlet, **kw)

        # Raise on lookup error
        msg = "No viewlet %s registered with manager %s" % \
            (viewlet_name, manager_name)
        raise RuntimeError, msg

    def macroContent(self, macropath, **kw):
        'Renders a macro and returns its text'
        path = macropath.split('/')
        if len(path) < 2 or path[-2] != 'macros':
            raise RuntimeError, 'Path must end with macros/name_of_macro (%s)' % (repr(macropath), )
        # needs string, do not tolerate unicode (causes but at traverse)
        jointpath = '/'.join(path[:-2]).encode('ascii')

        # put parameters on the request, by saving the original context
        self.request.form, orig_form = kw, self.request.form
        content = self._macroContent(
                    provider=jointpath, 
                    macro_name=path[-1],                  
                    **kw
                    )
        self.request.form = orig_form

        return content

class SylvesterKssView(BaseSylvesterKssView):

    @kssactionplus
    def tweet(self): 
        context = aq_inner(self.context)
        view = context.restrictedTraverse('@@collective.sylvester.dashboard')

        message = context.REQUEST.form['message'].strip()
        view.twitter.PostUpdate(message, handle_error=False)

        # xxx: caching issue! python-twitter caches results for a minute
        html = self.macroContent(
                '@@collective.sylvester.dashboard/macros/update_form',
                view=view)

        ksscore = self.getCommandSet('core')
        selector = ksscore.getHtmlIdSelector('collective-sylvester-dashboard-tweet-form')
        ksscore.replaceHTML(selector, html)

        kssplone = self.getCommandSet('plone')
        msg = _("Your message has been sent")
        kssplone.issuePortalMessage(msg, msgtype='info')

    @kssactionplus
    def dashboardNavigate(self, viewletname): 
        """
        Load content area of dashboard.
        """
        context = aq_inner(self.context)   
        view = context.restrictedTraverse('@@collective.sylvester.dashboard')

        if viewletname in ('statuses',):
            html = self.macroContent(
                '@@collective.sylvester.dashboard/macros/%s' % viewletname,
                view=view)
        else:
            html = self.viewletMacroContent(                    
                    'collective.sylvester.dashboardmanager', 
                    viewletname, 
                    'main')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getHtmlIdSelector(
            'collective-sylvester-dashboard-content')
        ksscore.replaceInnerHTML(selector, html)

        # Update the menus
        selector = ksscore.getCssSelector(
            'div.collective-sylvester-dashboard-navigation a')
        ksscore.removeClass(selector, 'selected')
        selector = ksscore.getHtmlIdSelector(
            'collective-sylvester-dashboard-navigation-%s' % viewletname)
        ksscore.addClass(selector, 'selected')

    @kssactionplus
    def refreshFriendlet(self, friend_id): 
        """
        Refresh a single friendlet

        xxx: not currently used and may be broken
        """
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')

        view = context.restrictedTraverse('@@collective.sylvester.dashboard')
        friend = view.twitter.GetUser(friend_id, handle_error=False)
        html = self.viewletMacroContent(                    
                'collective.sylvester.friendletmanager', 
                'collective.sylvester.friendlet', 
                'body',
                friend=friend)
        selector = ksscore.getHtmlIdSelector(
            'collective-sylvester-friendlet-friend%s' % friend_id) 
        ksscore.replaceHTML(selector, html)

    @kssaction
    def cachewarmer(self):
        """
        Do a few common calls to twitter. The results are not important.
        Doing these calls periodically ensures that results are always 
        available from RAM.
        """
        context = aq_inner(self.context)
        view = context.restrictedTraverse('@@collective.sylvester.dashboard')
        # This method is RAM-cached by the view
        view.GetFriendsTimeline()

        # Do the same for methods defined by pluggable viewlets
        for viewlet in view.getPluggableViewlets():
            if hasattr(viewlet, 'keepfresh'):
                getattr(viewlet, 'keepfresh')()
