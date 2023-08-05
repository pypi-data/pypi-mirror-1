### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The filterannotation adapter

$Id: filterannotableadapter.py 49136 2008-01-03 02:05:48Z cray $
"""
__author__  = "Anton Oprya, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49136 $"
from ng.app.rubricator.filterannotation.filterannotation import FilterAnnotation
from zope.annotation.interfaces import IAnnotations 

from interfaces import filterannotationkey

def FilterAnnotableAdapter(context) :
    return IAnnotations(context).setdefault(filterannotationkey,FilterAnnotation())


   

