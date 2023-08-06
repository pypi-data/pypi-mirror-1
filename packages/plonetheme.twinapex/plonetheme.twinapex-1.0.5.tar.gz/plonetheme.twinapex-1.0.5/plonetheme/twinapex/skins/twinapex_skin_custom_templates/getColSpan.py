## Script(Python) ""
##bind container=container
##bind context=context
##title=Calculate main table colspan
##parameters=sr,sl

colspan = 1

if sr:
    colspan += 1
    
if sl:
    colspan += 1

return colspan