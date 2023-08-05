### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RulesetEvaluator Vocabulary

$Id: rulesetevaluatorvocabulary.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov,2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm

from ng.app.rubricator.rulesetevaluator.interfaces import IRulesetevaluator
import zope.app.zapi

def RulesetEvaluatorVocabulary(context):
    """Get utitlity vocabulary for IRulesetevaluator"""
    utils = zope.app.zapi.getUtilitiesFor(IRulesetevaluator, context)
    return SimpleVocabulary.fromValues(dict(utils).keys())
