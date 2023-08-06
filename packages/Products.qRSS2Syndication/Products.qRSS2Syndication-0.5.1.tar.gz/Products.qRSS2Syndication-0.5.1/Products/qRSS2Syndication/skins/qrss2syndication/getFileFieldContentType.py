## Script (Python) "getAudioFiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= object=None
##title=
##
if not object:
    return None
from Products.qRSS2Syndication.utils import getFileContentType
return getFileContentType(object)