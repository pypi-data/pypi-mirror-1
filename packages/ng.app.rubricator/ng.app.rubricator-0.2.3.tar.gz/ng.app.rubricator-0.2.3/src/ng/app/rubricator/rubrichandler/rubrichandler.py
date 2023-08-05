### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of functions used to dispatch events to 
rubricalgorithm utility, to rubricate new INews objects

$Id: rubrichandler.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Arvid, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"
__date__ = "$Date: 2008-01-21 15:23:14 +0300 (Пнд, 21 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.component import ComponentLookupError
from ng.app.rubricator.rubricalgorithm.interfaces import IRubricAlgorithm
from ng.app.rubricator.rubricalgorithm.rubricalgorithm import RubricAlgorithm
import zope.app.zapi

class RubricAlgorithmNotFound(Exception):
    pass

def handleAdded(object,event) :
    try :
        sm = zope.app.zapi.getSiteManager(object)
        utilities = sm.getAllUtilitiesRegisteredFor(IRubricAlgorithm)
        if not utilities :
            raise RubricAlgorithmNotFound

        for algorithm in utilities:
            algorithm.place(object)
            
    except ComponentLookupError,msg :
        print "ComponentLookupError:", msg

def handleModified(object,event) :
    try :
        sm = zope.app.zapi.getSiteManager(object)
        utilities = sm.getAllUtilitiesRegisteredFor(IRubricAlgorithm)
        if not utilities :
            raise RubricAlgorithmNotFound
    
        for algorithm in utilities:
            algorithm.place(object)
        
    except ComponentLookupError,msg :
        print "ComponentLookupError:", msg

def handleRemoved(object,event) :
    try :
        pass
    except ComponentLookupError:
        pass
        