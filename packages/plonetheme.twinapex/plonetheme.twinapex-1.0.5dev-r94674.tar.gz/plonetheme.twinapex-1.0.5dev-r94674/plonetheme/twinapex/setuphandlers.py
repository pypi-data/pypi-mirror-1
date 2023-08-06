"""
    
    Run after Generic XML setup.
    
    Add new Kupu styles - can't use kupu.xml, because it is not additive,
    but replaces all styles once.
    
    http://www.twinapex.com

"""

__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import string
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

paragraph_styles = [
    "Subheading (blue)|h3|blue",
    "Bullet (grey)|li|grey-bullet",
    "Bullet (orange)|li|orange-bullet",    
    "Bullet (blue)|ul|blue-bullet",    
    "Box (grey)|p|grey-box",
    "Paragraph w/separator line|p|separator",
    "Yellow text|span|yellow-text",
    "Heading cell (grey)|th|grey-heading",    
]

table_classnames =[
    "twinapex-table orange-table|Orange heading",
    "twinapex-table blue-table|Blue heading",
    "twinapex-table grey-all|Grey background"
]

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profil
    """
        
    site = context.getSite()
    
    out = StringIO()
    
    print >> out, "Installing additional Kupu styles"
    
    kupu = site.kupu_library_tool
    for s in paragraph_styles:
        # plonelibrarytool.py line 823
        s = s.strip()
        if not s in kupu.paragraph_styles:
            kupu.paragraph_styles.append(s)
            print >> out, "Installed style:" + s

    for s in table_classnames:
        # plonelibrarytool.py line 823
        s = s.strip()
        if not s in kupu.table_classnames:
            kupu.table_classnames.append(s)
            print >> out, "Installed table class:" + s
    
            
    return out.getvalue()
    
