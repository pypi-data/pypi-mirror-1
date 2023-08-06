__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"

from zope import schema
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

#from collective.contentleadimage import LayoutImageMessageFactory as _

class ILayoutImageable(Interface):
    """ marker interface """
    