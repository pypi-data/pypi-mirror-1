### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based rubricalgorithm package

$Id: interfaces.py 51592 2008-08-31 21:42:37Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 51592 $"

from zope.interface import Interface
from zope.schema import Field, Text, Tuple, TextLine
from zope.app.container.interfaces import IContained
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ContainerTypesConstraint

class IRubricateAble(Interface) :
    """ Interface to mark object to rubricate """

class IRubricAlgorithmDo(Interface):
    """ A rubric algorithm interface """

    def rubricateAll(ob):
        """Link all object into rubrics"""

    def cleanAll() :
        """Remove link to all objects from rubrics"""
        
    def rubricateTo(ob):
        """Link object into rubrics"""

    def cleanTo() :
        """Remove link to object into rubrics"""

class IRubricAlgorithmContained(IContained):
    """Interface that specifies the type of objects that can contain RubricAlgoritmh"""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager, ISiteManagementFolder))


class IRubricAlgorithmError(Interface) :
    name = Text()
    args = Tuple(value_type=TextLine())
    
    