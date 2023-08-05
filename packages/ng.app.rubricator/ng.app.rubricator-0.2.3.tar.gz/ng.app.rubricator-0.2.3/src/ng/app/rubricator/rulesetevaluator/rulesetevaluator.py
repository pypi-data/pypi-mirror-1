### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The rulesetevaluator class.

$Id: rulesetevaluator.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.interface import implements
from zope.app.container.contained import Contained
from interfaces import IRulesetevaluator, IRulesetevaluatorContained
from ng.app.rubricator.filterannotation.interfaces import IFilterAnnotable, IFilterAnnotation
import re

parser = re.compile(
    """(?P<prefix>[^\s]+)"""
    """(\s+("(?P<argument0>[^"]+)"|(?P<argument1>[^\s]+)))?"""
    """(\s+("(?P<argument2>[^"]+)"|(?P<argument3>[^\s]+)))?"""
    """(\s+("(?P<argument4>[^"]+)"|(?P<argument5>[^\s]+)))?"""
    """(\s+("(?P<argument6>[^"]+)"|(?P<argument7>[^\s]+)))?"""
    """(\s+("(?P<argument8>[^"]+)"|(?P<argument9>[^\s]+)))?"""
    """\s+(?P<attr>[^\s]+)"""
).match

class InvalidPredicateError(AttributeError):
    pass

class Rulesetevaluator(Contained):
    """Evaluator for Ruleset"""
   
    implements(IRulesetevaluator, IRulesetevaluatorContained)
    
    def eval(self, rubric, ob):
        """Evaluate an evaluator"""
        try :
            ruleset = IFilterAnnotation(rubric).ruleset
        except TypeError,msg :
            print TypeError,msg
            return True

        if ruleset is None:
            return True

        for rule in ruleset:
            d = parser(rule).groupdict()
            attr = d["attr"]
            prefix = d["prefix"]
            tokens = [ d["argument%s" % x] for x in range(0,10) if d.get("argument%s" % x,None)]

            try:
                f = getattr(self, "handle_%s" % prefix)
            except AttributeError:
                raise InvalidPredicateError(prefix) 
            
            try :
                if f(ob, attr, *tokens):
                    return True
            except TypeError,msg :
                print "Invalid ruleset,1:", rule, msg
                #raise InvalidPredicateError(prefix) 
            except Exception,msg :
                print "Invalid ruleset,2:",msg, rule
                                
                                
        return False
    
    def handle_EQ(self, ob, attr, value):
        """Handle EQ predicate"""
        return getattr(ob, attr) == value

    def handle_NE(self, ob, attr, value):
        """Handle NE predicate"""
        return getattr(ob, attr) == value
        
    def handle_IN(self, ob, attr, value):
        """Handle IN predicate"""
        return value in getattr(ob, attr)

    def handle_NOTIN(self, ob, attr, value):
        """Handle NOTIN predicate"""
        return value not in getattr(ob, attr)
        