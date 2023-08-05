### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of functions used to dispatch events to 
newsrefbackreference storage, to index newsref objects 

$Id: newsrefhandler.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"

from zope.component import ComponentLookupError
from zope.app import zapi
from ng.app.rubricator.newsref.newsrefbackreference.interfaces import INewsRefBackReference
from ng.app.rubricator.newsref.newsref.interfaces import INewsRef

def handleAdd(ob,event) :
    try :
        for (name,br) in zapi.getUtilitiesFor(INewsRefBackReference, ob) :
            br.handleAdd(ob)
    except ComponentLookupError,msg :
        print "Could't find INewsBackReference:",msg
    
def handleDel(ob,event) :
    try :
        for (name,br) in zapi.getUtilitiesFor(INewsRefBackReference, ob) :
            br.handleDel(ob)
    except ComponentLookupError,msg :
        print "Could't find INewsBackReference:",msg
        