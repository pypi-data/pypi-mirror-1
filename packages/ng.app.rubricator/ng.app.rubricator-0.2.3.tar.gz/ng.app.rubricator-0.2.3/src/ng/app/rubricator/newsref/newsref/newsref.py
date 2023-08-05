### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newsref class.

$Id: newsref.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Ischenko Valera, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.interface import implements
from persistent import Persistent
from interfaces import INewsRef

from zope.app.intid.interfaces import IIntIds
from zope.component import getSiteManager
from zope.app.container.contained import Contained
from zope.app.zapi import getSiteManager
from zope.app.container.interfaces import IContained

class NewsRef(Persistent, Contained):
    __doc__ = INewsRef.__doc__

    implements(INewsRef, IContained)
    
    def __init__(self, id):
        self.id = id
        
    