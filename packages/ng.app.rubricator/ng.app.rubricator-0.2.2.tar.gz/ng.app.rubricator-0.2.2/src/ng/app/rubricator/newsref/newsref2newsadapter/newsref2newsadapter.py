### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newsref2newsadapter adapter.

$Id: newsref2newsadapter.py 49136 2008-01-03 02:05:48Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49136 $"
__date__ = "$Date: 2008-01-03 05:05:48 +0300 (Чтв, 03 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from ng.app.rubricator.newsref.newsref.interfaces import INewsRef
from zope.app.intid.interfaces import IIntIds
from zope.interface import implements
from zope.app.zapi import getSiteManager
from zope.component import ComponentLookupError

def NewsRef2NewsAdapter(newsRef):
    """Adapts a INewsRef to INews"""
    try :
        intids = getSiteManager(newsRef).getUtility(IIntIds)
    except ComponentLookupError,msg :
        print "IIntIds Lookup Error",msg
        raise
        
    return intids.getObject(newsRef.id)
    