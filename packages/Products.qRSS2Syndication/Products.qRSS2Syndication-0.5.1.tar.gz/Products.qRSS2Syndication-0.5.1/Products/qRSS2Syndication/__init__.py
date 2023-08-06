from AccessControl import allow_module
from Products.CMFCore.DirectoryView import registerDirectory, registerFileExtension
from config import GLOBALS

allow_module('Products.qRSS2Syndication.utils.py')

PROJECTNAME = "qRSS2Syndication"
SKINS_DIR='skins'         


registerDirectory(SKINS_DIR , GLOBALS)