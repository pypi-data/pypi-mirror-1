### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newsrefbackreference class.

$Id: newsrefbackreference.py 49134 2008-01-03 01:49:24Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49134 $"

from zope.interface import implements
from interfaces import INewsRefBackReference,INewsRefBackReferenceContained,INewsRefBackReferenceContainer
from zope.app.container.btree import BTreeContainer
from newsrefbackreferenceitems import NewsRefBackReferenceItems
from zope.app import zapi
from zope.app.intid.interfaces import IIntIds


class NewsRefBackReference(BTreeContainer):
    __doc__ = INewsRefBackReference.__doc__

    implements(INewsRefBackReference,INewsRefBackReferenceContained,INewsRefBackReferenceContainer)
    
    def handleAdd(self,ref) :
        name = "c%016u" % ref.id
       
        try :
            items = self[name]   
        except KeyError :
            items = self[name] = NewsRefBackReferenceItems()
            
        items.append("c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ref))            
        
    def handleDel(self,ref) :
        name = "c%016u" % ref.id
       
        try :
            items = self[name]   
        except KeyError :
            return
            
        items.remove("c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ref))        
        
    def handleDelOb(self,ob) :
        self.handleCleanOb(ob)
        name = "c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ob)
        try :
            del(self[name])
        except KeyError, msg :
            print "Can't clean object from newsbackreference index becouse of",msg            

    def handleCleanOb(self,ob) :
        name = "c%016u" % zapi.getUtility(IIntIds, self.newsRefId).getId(ob)
        try :
            items = self[name]   
        except KeyError :
            return

        for item in list(items) :
            try :
                ref = zapi.getUtility(IIntIds, self.newsRefId).getObject(int(item[1:]))
                del(ref.__parent__[ref.__name__])
                
            except KeyError,msg :
                print "Can't remove reference becouse of",msg

                    