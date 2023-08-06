## Script (Python) "getAudioFiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=
##
from Products.qRSS2Syndication.utils import listSyndicatableContent
if not obj:
   obj = context
if hasattr(context,'synContentValues') or context.portal_type=='Topic':
   count = int(context.portal_syndication.getMaxItems(obj))
   res = context.portal_syndication.getSyndicatableContent(obj)
   # has to check and cut number of items to be displayed 
   # to prevent feed bloat 
   count = count<len(res) and count or len(res)
   res = res[:count]
else:
   res = listSyndicatableContent(obj) 
return res
