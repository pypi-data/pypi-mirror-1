__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter


class FooterViewlet(ViewletBase):
    render = ViewPageTemplateFile('footer.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.footer_items = context_state.actions().get('footer', None)

class PathBarViewlet(ViewletBase):
    render = ViewPageTemplateFile('path_bar.pt')
    
    def update(self):
        super(PathBarViewlet, self).update()

        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()

from webcouturier.dropdownmenu.browser.dropdown import DropdownMenuViewlet
class GlobalSectionsViewlet(DropdownMenuViewlet):

    render = ViewPageTemplateFile('sections.pt')  
        
    def getRollOverImage(self, id, onmouseover=False):
        portal_url = self.context.portal_url()
        
        if onmouseover:
            name = id + "_rollover.gif"            
        else:
            name = id + ".gif"
        
        return "%s/++resource++plonetheme.twinapex.images/buttons/%s" % (portal_url, name)
    
