### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The filterannotation

$Id: filterannotation.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from persistent import Persistent
from zope.interface import implements
from interfaces import IFilterAnnotation

class FilterAnnotation(Persistent) :
    __doc__ = IFilterAnnotation.__doc__
    implements(IFilterAnnotation)

    # See noteannotation.interfaces.INoteAnnotation
    ruleset = []

    def __init__(self,*kv,**kw) :
        self.ruleset = []
        super(FilterAnnotation,self).__init__(*kv,**kw) 