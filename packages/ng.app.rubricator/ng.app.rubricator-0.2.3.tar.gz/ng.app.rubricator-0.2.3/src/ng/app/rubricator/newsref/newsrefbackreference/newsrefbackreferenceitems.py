### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newsrefbackreferenceitem class.

$Id: newsrefbackreferenceitems.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.interface import implements
from interfaces import INewsRefBackReferenceItems,INewsRefBackReferenceItemsContained
from persistent.list import PersistentList
from zope.app.container.contained import Contained

class NewsRefBackReferenceItems(Contained,PersistentList):
    __doc__ = INewsRefBackReferenceItems.__doc__

    implements(INewsRefBackReferenceItems,INewsRefBackReferenceItemsContained)
    
    def append(self,item) :
        if item not in self :
            super(NewsRefBackReferenceItems,self).append(item)
        
        
        
        
            