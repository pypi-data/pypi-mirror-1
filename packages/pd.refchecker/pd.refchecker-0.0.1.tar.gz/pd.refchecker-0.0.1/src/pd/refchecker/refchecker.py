### -*- coding: utf-8 -*- #############################################
#######################################################################                                                 #

"""Class adapter for the Zope 3 based search package

$Id: refchecker.py 49399 2008-01-13 07:24:23Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL"
__version__ = "$Revision: 49399 $"
__date__ = "$Date: 2008-01-13 10:24:23 +0300 (Вск, 13 Янв 2008) $"
 
from zope.interface import implements
from interfaces import ISearchReference

import re

find = re.compile("(https?://[A-Za-z0-9_\.\-]+(?:[0-9]+)?/[^\"\s<,\)]*)",re.M|re.I|re.U)

class SearchReferenceAdapter(object) :
    """Interface for index objects"""
    implements(ISearchReference)    

    def __init__(self,context) :
        self.context = context
      
    @property
    def reference(self) :
        return re.findall(find,self.context.common)
