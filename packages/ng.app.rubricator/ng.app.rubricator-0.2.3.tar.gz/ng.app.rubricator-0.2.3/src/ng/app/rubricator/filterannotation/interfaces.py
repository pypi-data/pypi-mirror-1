### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based filterannotation package

$Id: interfaces.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Anton Oprya"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"


from zope.schema import Text, TextLine, Datetime, Tuple

from zope.interface import Interface

class IFilterAnnotable(Interface) :
    pass

class IFilterAnnotation(Interface) :

    ruleset = Tuple(
        title = u'Rule Set',
        description = u"Some rules",
        value_type = TextLine(),
        )

    
filterannotationkey="rulesetannotations.rulesetannotations.RuleSet"
    