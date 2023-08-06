### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReindexEdit MixIn class for the Zope 3 based rubricalgorithm package

$Id: reindex.py 51592 2008-08-31 21:42:37Z cray $
"""
__author__  = "Andrey Orlov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51592 $"
__date__ = "$Date: 2008-09-01 01:42:37 +0400 (Пнд, 01 Сен 2008) $"
 
from zope.interface import Interface
                
class ReindexEdit(object) :

    def update(self) :
        super(ReindexEdit, self).update()
        if "reindex" in self.request :
            self.context.rubricateAll()

        if "clean" in self.request :
            self.context.cleanAll()
                    

        
        
        
