### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The vocabulary of newsrefbackreference items.

$Id: vocabulary.py 49134 2008-01-03 01:49:24Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49134 $"

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm

from interfaces import INewsRefBackReference
import zope.app.zapi

def Vocabulary(context):
    """Get utitlity vocabulary for INewsRefBackReference"""
    utils = zope.app.zapi.getUtilitiesFor(INewsRefBackReference, context)
    return SimpleVocabulary.fromValues(dict(utils).keys())
