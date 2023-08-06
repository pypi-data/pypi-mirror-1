## Script (Python) "getAudioFiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= object=None
##title=
##
from Products.qRSS2Syndication.utils import getRSS2Properties
res=getRSS2Properties(context)
return res