### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based rubricator package

$Id: interfaces.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"
 
from zope.interface import Interface

class IRubricateAble(Interface) :
    """ Marker to sign class as Rubricatable """
    pass
    