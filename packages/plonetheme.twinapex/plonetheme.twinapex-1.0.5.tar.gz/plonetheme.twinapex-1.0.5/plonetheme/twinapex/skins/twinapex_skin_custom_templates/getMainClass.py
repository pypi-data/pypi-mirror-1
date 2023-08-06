## Script(Python) ""
##bind container=container
##bind context=context
##title=Calculate main table colspan
##parameters=sr,sl

# FUCKING HACK FOR THE SAKE OF IE6

# google ie6 colspan width css bug

if sl and sr:
    return "with-left-right-portlets"
elif sr:
    return "with-right-portlets"
elif sl:
    return "with-left-portlets"
else:
    return "with-no-portlets"

