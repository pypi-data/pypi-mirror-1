__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"

from Products.Five.browser import BrowserView

class HeaderView(BrowserView):
    
    def hasHeader(self):
        return self.hasHeaderAnimation() or self.hasHeaderImage()
        
    def hasHeaderAnimation(self):
        
        context = self.context
        if not hasattr(context, "getField"):
            return False
                
        field = context.getField("headerAnimation")
        if field is not None:
            animation = field.get(self.context)    
        else:
            return False
            
        if animation != None and animation != '' and animation.getSize() > 0:
            return True
        
        return False
        
    def hasHeaderImage(self):
        
        context = self.context
        if not hasattr(context, "getField"):
            return False
                
        field = context.getField("headerImage")
        if field is not None:
            data = field.get(self.context)    
        else:
            return False
        
        if data != None and data != '' and data.getSize() > 0:
            return True        
        
    def isFullWidthLayout(self):
        
        context = self.context
        if not hasattr(context, "getField"):
            return False
                
        field = context.getField("fullWidth")
        if field is not None:
            value = field.get(self.context)    
        else:
            return False
        
        return value
    
    def getCSSClasses(self):
        """ CSS Classes applied to main table. """
        classes = []
        if self.hasHeader():
            classes.append('header-layout')
        if self.isFullWidthLayout():
            classes.append("full-width")
            
        return " ".join(classes)
    
    def getHeaderWidth(self):
        """ Width used for Flash animation. """
        if self.isFullWidthLayout():
            return 920
        else:
            return 730
        

    