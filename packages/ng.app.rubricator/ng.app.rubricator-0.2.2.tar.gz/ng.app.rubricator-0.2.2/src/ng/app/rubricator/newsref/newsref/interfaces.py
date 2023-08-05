### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based newsref package

$Id: interfaces.py 49133 2008-01-03 01:37:53Z cray $
"""
__author__  = "Ischenko Valera"
__license__ = "GPL"
__version__ = "$Revision: 49133 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Int, List, Object
from zope.app.container.interfaces import IContained, IContainer

class INewsRef(Interface):
    """ A newsref interface """
    
    id = Int (
           title=u"Unique id",
           description=u"Unique id",
           default=0,
           required=True,
           readonly=True)
                                                


