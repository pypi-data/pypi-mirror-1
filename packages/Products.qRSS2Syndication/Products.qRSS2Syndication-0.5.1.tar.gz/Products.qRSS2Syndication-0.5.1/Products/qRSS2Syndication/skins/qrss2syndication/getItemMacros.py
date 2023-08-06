## Script (Python) "getAudioFiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=etype
##title=
##

template_id = etype.lower()+'_item'
template = getattr(context, template_id, None)
if template:
    return template.macros['item']
else:
    return context.default_item.macros['item']