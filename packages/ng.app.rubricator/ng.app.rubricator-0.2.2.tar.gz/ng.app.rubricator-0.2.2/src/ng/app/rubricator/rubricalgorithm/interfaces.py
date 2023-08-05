### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based rubricalgorithm package

$Id: interfaces.py 49133 2008-01-03 01:37:53Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49133 $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice, Tuple
from zope.app.container.interfaces import IContained, IContainer
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ContainerTypesConstraint

class IRubricAlgorithm(Interface):
    """ A rubric algorithm interface """

    rulesetEvaluator = Choice(title = u'Name of Ruleset Evaluator',
                        description = u'Name of Ruleset Evaluator Utility',
                        default = None,
                        required = True,
                        vocabulary = 'RulesetEvaluatorNames'
                        )
        
    backreference = Choice(title = u'Name of NewsRefBackeference',
                        description = u'Name of NewsRefBackeference Utility',
                        default = None,
                        required = True,
                        vocabulary = 'NewsRefBackReferenceVocabulary'
                        )
        
    
    newsRefId = Choice(title = u'Name of Int Ids',
                        description = u'Name of IntIds utility, user for registering news in rubrics',
                        default = None,
                        required = True,
                        vocabulary = 'IntIdsNames'
                        )
    
    rootRubricPath = TextLine(title = u'Root Rubric Path',
                        description = u'Path for Root Rubric',
                        default = u'',
                        required = True,
                        )
        
    interface = Choice(title = u'Name of Interface',
                        description = u'Objects will be adapted to this interface',
                        default = None,
                        required = True,
                        vocabulary = 'Interfaces'
                        )
                        
    def place(context, news):
        """Places a news into rubrics"""

class IRubricAlgorithmContained(IContained):
    """Interface that specifies the type of objects that can contain CacheStore."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager, IRubricAlgorithm, ISiteManagementFolder))

class IConfigureError(Interface) :
    name = Text()
    
    args = Tuple(value_type=TextLine())
    
    