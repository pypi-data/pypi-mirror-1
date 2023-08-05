### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The rulehandler dispatcher

$Id: rulehandler.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from ng.app.rubricator.filterannotation.interfaces import IFilterAnnotable, IFilterAnnotation, filterannotationkey
from ng.app.rubricator.filterannotation.filterannotation import FilterAnnotation


def ruleHandler(object, event) :
    """handle event before traverse"""
    ruleset = IFilterAnnotation(object).ruleset[:]
    
    event.request.annotations.setdefault(filterannotationkey, FilterAnnotation()).ruleset.extend(ruleset)
