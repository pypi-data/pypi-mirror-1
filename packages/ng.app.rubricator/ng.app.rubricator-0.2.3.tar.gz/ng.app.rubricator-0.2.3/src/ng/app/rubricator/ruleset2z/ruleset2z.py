### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The ruleset2z adapter

$Id: ruleset2z.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.interface import implements
from persistent import Persistent
from interfaces import IZ

from ng.app.rubricator.rulesetevaluator.rulesetevaluator import parser

class RuleSetParserBase(object):
    """Parser of Rule Sets"""

    def parser(self,ruleset) :
        for rule in ruleset:
            d = parser(rule).groupdict()
            attr = d["attr"]
            prefix = d["prefix"]
            tokens = [ d["argument%s" % x] for x in range(0,10) if d.get("argument%s" % x,None)]

            try:
                f = getattr(self, "handle_%s" % prefix)
            except AttributeError:
                raise InvalidPredicateError(prefix) 
            
            yield (f, attr, tokens)

class Z(dict) :
    implements(IZ)

class RuleSet2Z(RuleSetParserBase)  :

    def __call__(self,ruleset) :
        res = {}
        for f,attr,tokens in self.parser(ruleset.ruleset) :
            f(res, str(attr), *tokens)
        return Z(res)
        
    def handle_EQ(self, res, attr, value):
        """Handle EQpredicate"""
        res[attr]=(value,value)
        
    def handle_IN(self, res, attr, value):
        """Handle IN predicate"""
        try :
            s = res[attr] + " or "
        except KeyError :
            s = value
        else :
            s = s + value
        res[attr] = s

ruleset2z = RuleSet2Z()
