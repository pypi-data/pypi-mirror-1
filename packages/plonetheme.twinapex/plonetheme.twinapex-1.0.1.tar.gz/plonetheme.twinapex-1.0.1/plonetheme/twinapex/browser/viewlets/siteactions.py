__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"

from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet

from plone.app.layout.globals.interfaces import IViewView

from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from cgi import escape
from urllib import quote_plus

from plone.app.layout.viewlets.common import ViewletBase


class SiteActionsViewlet(ViewletBase):
    """SiteActions and SeachBox all together.
    
    Overridden to use our custom template.
    """
#    implements(IViewlet)

    render = ViewPageTemplateFile('site_actions.pt')

    def __init__(self, context, request, *args, **kw):
        ViewletBase.__init__(self, context, request, *args, **kw)
        utool = getToolByName(context, 'portal_url')
        self.url = utool()
        pass
    
    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        

        self.site_actions = context_state.actions().get('site_actions', None)

