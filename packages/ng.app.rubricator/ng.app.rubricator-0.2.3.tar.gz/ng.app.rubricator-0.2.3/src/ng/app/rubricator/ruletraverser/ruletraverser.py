### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RuleTraverser class for the Zope 3 based rubricator package

$Id: ruletraverser.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Valera Ischenko"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.publisher.interfaces import NotFound 
from zope.app import zapi 
from zope.app.container.traversal import ContainerTraverser 
from ng.app.rubricator.filterannotation.interfaces import IFilterAnnotation, filterannotationkey

class RuleTraverser(ContainerTraverser):
    """Traverses an container items"""
   
    __used_for__ = IFilterAnnotation

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.browser.IBrowserPublisher""" 
        
        ob = self.context.get(name, None)
        rules = IFilterAnnotation(ob)
        request.annotations.setdefault(filterannotationkey, []).append(rules)
        
        return super(RuleTraverser, self).publishTraverse(request, name)

        
        
