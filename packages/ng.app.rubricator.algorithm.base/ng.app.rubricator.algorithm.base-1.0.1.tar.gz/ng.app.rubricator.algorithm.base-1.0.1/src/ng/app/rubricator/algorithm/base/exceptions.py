### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The exceptions for rubricator algorithm

$Id: exceptions.py 51592 2008-08-31 21:42:37Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51592 $"

from zope.interface import implements
from interfaces import IRubricAlgorithmError

class RubricAlgorithmError(Exception) :
    implements(IRubricAlgorithmError)
    
    def __init__(self,name,*kv) :
        self.name = name
        self.args = kv
                    
