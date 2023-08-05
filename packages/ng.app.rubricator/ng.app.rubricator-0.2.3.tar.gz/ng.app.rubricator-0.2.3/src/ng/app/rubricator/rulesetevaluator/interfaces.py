### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based rulesetevaluator package

$Id: interfaces.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.app.container.interfaces import IContained, IContainer
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ContainerTypesConstraint

class IRulesetevaluator(Interface):
    """ A rulesetevaluator interface """
    
    def eval(ruleset, ob):
        """Evaluate an evaluator"""
    
class IRulesetevaluatorContained(IContained):
    """Interface that specifies the type of objects that can contain Rulesetevaluator."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager, ISiteManagementFolder))
