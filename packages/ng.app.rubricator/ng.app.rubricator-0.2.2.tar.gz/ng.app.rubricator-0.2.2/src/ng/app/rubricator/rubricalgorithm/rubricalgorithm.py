### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The rubricalgorithm class.

$Id: rubricalgorithm.py 49136 2008-01-03 02:05:48Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "GPL"
__version__ = "$Revision: 49136 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContainer
from interfaces import IRubricAlgorithm, IRubricAlgorithmContained, IConfigureError
import zope.app.zapi
from ng.app.rubricator.rulesetevaluator.interfaces import IRulesetevaluator
from zope.app.folder.interfaces import IFolder
from zope.app.intid.interfaces import IIntIds
from ng.app.rubricator.newsref.newsref.newsref import NewsRef
from ng.app.rubricator.newsref.newsrefbackreference.interfaces import INewsRefBackReference
from zope.app.container.interfaces import INameChooser



class ConfigureError(Exception) :
    implements(IConfigureError)
    name = u"Configure Error"

class InvalidRubricObjectError(ConfigureError):
    name = u"InvalidRubricObjectError"

class RulesetEvaluatorNotFoundError(ConfigureError):
    name = u"RulesetEvaluatorNotFoundError"
    
class IntIdsNotFoundError(ConfigureError):
    name = u"IntIdsNotFoundError"

class Environment(object) :

    def __init__(self,context):
        self.sm = zope.app.zapi.getSiteManager(context)
        self.evaluator = self.sm.queryUtility(IRulesetevaluator, context.rulesetEvaluator)

        if self.evaluator is None:
            raise RulesetEvaluatorNotFoundError(context.rulesetEvaluator)
        
        self.intids = self.sm.queryUtility(IIntIds, context.newsRefId)

        if self.intids is None:
            raise IntIdsNotFoundError(context.newsRefId)
            
        self.root = zope.app.zapi.traverse(self.sm.__parent__, context.rootRubricPath)
        if not IContainer.providedBy(self.root) : 
            raise InvalidRubricObjectError(self.root)
            
class RubricAlgorithm(Contained, Persistent):
    """Rubricator for News into Rubrics with NewsRefs """

    implements(IRubricAlgorithm, IRubricAlgorithmContained)
    
    interface = u''

    """Name of ruleset evaluator utility"""
    rulesetEvaluator = None
        
    """Name of IntIds utility for placed NewsRefs"""
    newsRefId = None

    backreference = u''
    
    """Path for root rubric from root object"""
    rootRubricPath = u''
    
    def clean(self) :
        environment = Environment(self)
        for uid in environment.intids :
            news = environment.intids.getObject(uid)
            environment.sm.queryUtility(INewsRefBackReference, self.backreference).handleCleanOb(news)
                    
    def reindex(self) :
        environment = Environment(self)
        for uid in environment.intids :
            news = environment.intids.getObject(uid)
            self._place(environment, news)        
                    
    def place(self, news) :
        return self._place(Environment(self),news)

    def _place(self, environment, news):
        """Get a root rubric, then place a news with _subplace"""
        
        environment.sm.queryUtility(INewsRefBackReference, self.backreference).handleCleanOb(news)
    
        try :
            ob = self.interface(news)
        except TypeError,msg :
            print "Object",news,"incompatible with it rubricalgorithm"
        else:                                    
            self._subplace(environment.root, ob, news,  environment)
    
    def _subplace(self,rubric, ob, news, environment):
        """Place News into rubrics, that don't have an evaluated children"""
        
        placehere = True
        for subrubric in rubric.values():
            if IContainer.providedBy(subrubric) :
                if environment.evaluator.eval(subrubric, ob):
                    placehere = False
                    self._subplace(subrubric, ob, news, environment)

        if placehere :                
            ref = NewsRef(environment.intids.getId(news))
            rubric[INameChooser(rubric).chooseName(news.__name__,ref)] = ref
            
