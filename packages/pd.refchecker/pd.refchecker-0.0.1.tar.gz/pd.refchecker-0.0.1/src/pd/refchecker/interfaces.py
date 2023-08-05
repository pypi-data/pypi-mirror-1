### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49399 2008-01-13 07:24:23Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49399 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Tuple
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
                
class ISearchReference(Interface) :
    
    reference = Tuple()
                            