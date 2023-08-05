### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based rulehandler package

$Id: interfaces.py 49133 2008-01-03 01:37:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49133 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.app.container.interfaces import IContained, IContainer

class IRulehandler(Interface):
    """ A rulehandler interface """ 
    pass


