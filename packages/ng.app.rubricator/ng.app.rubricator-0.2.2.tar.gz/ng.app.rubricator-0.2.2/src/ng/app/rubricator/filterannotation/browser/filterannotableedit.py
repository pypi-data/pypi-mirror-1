### -*- coding: utf-8 -*- #############################################
#######################################################################
"""edit for filterannotation package

$Id: filterannotableedit.py 49136 2008-01-03 02:05:48Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49136 $"

from zope.schema import getFieldNames 
from ng.app.rubricator.filterannotation.interfaces import IFilterAnnotation

class FilterAnnotableEdit(object) :
    def getData(self,*kv,**kw) :
        self.na = IFilterAnnotation(self.context)
        return [ (x,getattr(self.na,x)) for x in  getFieldNames(IFilterAnnotation)]

    def setData(self,d,**kw) :
        for x in getFieldNames(IFilterAnnotation) :
            setattr(self.na,x,d[x])
        return True
        
