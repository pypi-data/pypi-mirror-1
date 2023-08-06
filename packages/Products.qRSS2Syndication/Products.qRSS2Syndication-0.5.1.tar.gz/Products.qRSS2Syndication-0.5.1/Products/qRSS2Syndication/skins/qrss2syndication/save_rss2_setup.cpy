## Controller Python Script "createObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters= rss2_types=(),only_published=0,include_subfolders=0, articles_number=20,REQUEST=None
##title=
##
if REQUEST:
  from Products.qRSS2Syndication.utils import setupRSS2Types
  status,message=setupRSS2Types(context,rss2_types,only_published,include_subfolders,articles_number,REQUEST)
return state.set(status=status, portal_status_message=message)
    