### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReindexEdit MixIn class for the Zope 3 based rubricalgorithm package

$Id: reindex.py 49606 2008-01-21 12:23:14Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49606 $"
__date__ = "$Date: 2008-01-21 15:23:14 +0300 (Пнд, 21 Янв 2008) $"
 
from zope.interface import Interface
                
class ReindexEdit(object) :

    def update(self) :
        super(ReindexEdit, self).update()
        if "reindex" in self.request :
            self.context.reindex()

        if "clean" in self.request :
            self.context.clean()
                    

        
        
        
