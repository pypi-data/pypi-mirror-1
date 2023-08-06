### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The handler definitions used to dispatch events to 
IRubricAlgoritmDo utility, to rubricate new IRubricatable objects

$Id: rubrichandler.py 51592 2008-08-31 21:42:37Z cray $
"""
__author__  = "AndreyOrlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51592 $"

from zope.component import ComponentLookupError
from ng.app.rubricator.algorithm.base.exceptions import IRubricAlgorithmError
from ng.app.rubricator.algorithm.base.interfaces import IRubricAlgorithmDo
from zope.app.zapi import getUtilitiesFor

def handleAdded(object,event) :
    print "added"
    for name,algorithm in getUtilitiesFor(IRubricAlgorithmDo) :
        algorithm.rubricateTo(object)

def handleModified(object,event) :
    print "modified"
    for name,algorithm in getUtilitiesFor(IRubricAlgorithmDo) :
        print name, algorithm
        algorithm.cleanTo(object)
        algorithm.rubricateTo(object)

def handleRemoved(object,event) :
    print "removed"
    for name,algorithm in getUtilitiesFor(IRubricAlgorithmDo) :
        algorithm.cleanTo(object)
        