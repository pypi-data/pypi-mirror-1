from zope.interface import implements
from zope.component import getUtility
from zope import schema

from plone.app.portlets.portlets import base

from plone.portlet.static import static 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlet.static import PloneMessageFactory as _

class IGreyStaticPortlet(static.IStaticPortlet):
    """ Defines a new portlet "grey static" which takes properties of the existing static text portlet. """
    pass

class GreyStaticRenderer(static.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('grey_static.pt')
    
class GreyStaticAssignment(static.Assignment):
    """ Assigner for grey static portlet. """
    implements(IGreyStaticPortlet)
    
class GreyStaticAddForm(static.AddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    def create(self, data):
        return GreyStaticAssignment(**data)    
