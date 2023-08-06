# Script(Python) "getHeaderImage"
##bind container=container
##bind context=context
##title=Get the 1st level container of the context or site root
##

attrs = [ "headerImage", "headerAnimation"]

# Content type does not support header image
for a in attrs:
    if not hasattr(context, a):
        break
    
img = context.getHeaderImage()
if img != None and img != '':
    return True

animation = context.getHeaderAnimation()
if animation != None and animation != '':
    return True



