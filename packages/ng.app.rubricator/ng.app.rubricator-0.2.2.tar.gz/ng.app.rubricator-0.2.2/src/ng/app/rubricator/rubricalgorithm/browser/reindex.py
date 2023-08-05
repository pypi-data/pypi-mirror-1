### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReindexEdit MixIn class for the Zope 3 based rubricalgorithm package

$Id: reindex.py 49134 2008-01-03 01:49:24Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49134 $"
__date__ = "$Date: 2008-01-03 04:49:24 +0300 (Чтв, 03 Янв 2008) $"
 
from zope.interface import Interface
                
class ReindexEdit(object) :

    def update(self) :
        super(ReindexEdit, self).update()
        if "reindex" in self.request :
            self.context.reindex()

        if "clean" in self.request :
            self.context.clean()
                    

        
        
        
