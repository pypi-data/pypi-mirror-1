### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The rubricalgorithm base class.

$Id: rubricalgorithmbase.py 51592 2008-08-31 21:42:37Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51592 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.zapi import getUtility
from zope.app.intid.interfaces import IIntIds
from ng.app.link.link import Link
from ng.app.link.linkbackreference.interfaces import ILinkBackReference
from zope.app.container.interfaces import INameChooser

from interfaces import IRubricAlgorithmDo, IRubricAlgorithmContained, IRubricateAble

class RubricAlgorithmBase(Contained, Persistent):
    """Base rubricator algorithm class """

    implements(IRubricAlgorithmDo, IRubricAlgorithmContained)
    
    def cleanAll(self) :
        getUtility(ILinkBackReference).cleanAll()
                    
    def rubricateAll(self) :
        self.cleanAll()
        intids = getUtility(IIntIds,context=self)
        for uid in intids :
            ob = intids.getObject(uid)
            if IRubricateAble.providedBy(ob) : 
                self.rubricateTo(ob)        
                    
    def rubricateTo(self, ob) :
        print "rubricateTo"
        return self.rubricate(getUtility(IIntIds,context=self).getId(ob),ob)

    def cleanTo(self,ob) :
        getUtility(ILinkBackReference,context=self).handleCleanOb(ob)
        
    def rubricate(self, id, ob) :
        return 
    
    def link(self,id,ob,rubric) :
        link = Link(id)
        rubric[INameChooser(rubric).chooseName(ob.__name__,link)] = link
            
