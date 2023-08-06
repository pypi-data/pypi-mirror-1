## Script(Python) "getHeaderImage"
##bind container=container
##bind context=context
##title=Get the 1st level container of the context or site root
##

#
# Iterate through parent folders to find content item named with
# id "headerimage". If not found, fallback to the default header image.
#

iter = context

while hasattr(iter, 'aq_parent'):
    
    if hasattr(iter, 'portal_type'):
        try:
            if iter.portal_type == "Folder":
                if "header-image" in iter:
                    return iter['header-image'].absolute_url()
        except:
            # Some evil permission magic
            pass
    
    parent = iter.aq_parent
    
    iter = parent
    
# Default to global header image
portal_url = context.portal_url 
return portal_url() + "/++resource++freearch.theme.images/header.jpg"
