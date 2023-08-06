from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Extensions.utils import  install_subskin
from Products.qRSS2Syndication.config import GLOBALS

def removeSkin(self, skins = []):
    if skins:
        skinstool = getToolByName(self, 'portal_skins')
        for skinName in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skinName)
            path = [i.strip() for i in  path.split(',')]
            for s in skins:
                if s in path:
                    path.remove(s)
            path = ','.join(path)
            skinstool.addSkinSelection(skinName, path)


def install(self):
    out = StringIO()
 
    # Add actionInfo icon to portal_actionicons. Delete old version before adding, if exist one.
    actionicons_tool = getToolByName(self, 'portal_actionicons')
    if actionicons_tool.queryActionInfo('plone', 'rss2syndication'):
        actionicons_tool.removeActionIcon('plone','rss2syndication')
    actionicons_tool.addActionIcon(category='plone', action_id='rss2syndication', 
                                   icon_expr='rss2_icon.png', title='RSS2 Syndication')

    # Add actionInfo  action to portal_actions. Delete old versions before adding, if exist one.
    action_tool = getToolByName(self, 'portal_actions')
    actions_id = [a.id for a in action_tool._actions]
    selections = [actions_id.index(a) for a in actions_id if a in ('rss2syndication','setup_rss2')]
    action_tool.deleteActions(selections=selections)


    action_tool.addAction(id='rss2syndication', name='RSS2 Syndication', action='string:$object_url/RSS2', 
                          condition='python: folder==object and portal.portal_syndication.isSyndicationAllowed(object)', permission=('View',), category='document_actions')
    action_tool.addAction(id='setup_rss2', name='RSS2 Setup', action='string:$object_url/setup_rss2', 
                          condition='python:portal.portal_syndication.isSyndicationAllowed(object)', permission=('Manage properties',), category='folder')

    install_subskin(self,out,GLOBALS)

    print >> out, "\nSuccessfully installed qRSS2Syndication."
    return out.getvalue()

def uninstall(self):
    action_tool = getToolByName(self, 'portal_actions')

    actions_id = [a.id for a in action_tool._actions]
    selections = [actions_id.index(a) for a in actions_id if a in ('rss2syndication','setup_rss2')]
    action_tool.deleteActions(selections=selections)

    actioniconstool = getToolByName(self, 'portal_actionicons')
    if actioniconstool.queryActionInfo('plone', 'rss2syndication'):
        actioniconstool.removeActionIcon('plone','rss2syndication')
    
    removeSkin(self, ('grss2syndication',))

    return 'qRSS2Syndication actionProvider successfully uninstalled'  
