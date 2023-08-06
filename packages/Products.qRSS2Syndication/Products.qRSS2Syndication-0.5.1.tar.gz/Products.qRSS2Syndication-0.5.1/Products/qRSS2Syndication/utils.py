from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base


def setupRSS2Types(context,
                    rss2_types = (),
                    only_published = 0,
                    include_subfolders = 0,
                    articles_number = 20,
                    REQUEST = None):
    """ Save all needed RSS2 properties into 'syndication_information' """
    obj=aq_base(context)
    status = 'success'
    message = 'Your changes have been saved'

    syInfo = getattr(obj, 'syndication_information', None)

    if syInfo is None:
        message = 'Syndication is Disabled'
        status = 'failed'
    syInfo.rss2_types = list(rss2_types)
    syInfo.only_published = only_published
    syInfo.include_subfolders = include_subfolders
    syInfo.max_items = int(articles_number)
    return status, message

def getRSS2Properties(context):
     """ Return directory of RSS2 properties from 'syndication_information' """
     obj=aq_base(context)
     syInfo = getattr(obj, 'syndication_information', None)
     syPropeties={}
     syPropeties['rss2_types'] = getattr(syInfo,'rss2_types',[])
     syPropeties['only_published'] = getattr(syInfo,'only_published',0)
     syPropeties['include_subfolders'] = getattr(syInfo,'include_subfolders',0)
     syPropeties['articles_number'] =int(getattr(syInfo,'max_items',20))
     return  syPropeties



def listSyndicatableContent(context):
    """ List folder contents - catalog query 
        * filtered types only
        * sort on effective
        * take only first 'articles_number' of elements """
    res = []
    ps = getToolByName(context,'portal_syndication')
    cpath = '/'.join(context.getPhysicalPath())
    syProperties = {}
    syProperties = getRSS2Properties(context)
    include_subfolders = 0
    if ps.isSyndicationAllowed(context):
        types = syProperties['rss2_types']
        only_published = syProperties['only_published']
        include_subfolders = syProperties['include_subfolders']
        articles_number = syProperties['articles_number']

        catalog = getToolByName(context,'portal_catalog')
        args = {'portal_type':types, 
              	'path':cpath,
                'sort_on':'effective',
                'sort_order':'reverse',}
        if only_published:
            args['review_state'] = 'published'
        if include_subfolders == 0:
            args['sort_limit'] = articles_number
        res=catalog.searchResults(args)
    path_length=len(cpath)+1
    res1=[]
    if include_subfolders == 0:
        for i in res :
            if i.getPath()[path_length:].find('/')<0:
                res1.append(i)
        res = res1[:articles_number]
    res = [r.getObject() for r in res]
    return res


def getFileContentType(context):
    """  !ATAudio specific only! Get the content type of file field method """
    return context.Schema()['file'].getContentType(context)