### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newsrefbackreferenceitem class.

$Id: newsrefbackreferenceitems.py 49134 2008-01-03 01:49:24Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49134 $"

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
        
        
        
        
            