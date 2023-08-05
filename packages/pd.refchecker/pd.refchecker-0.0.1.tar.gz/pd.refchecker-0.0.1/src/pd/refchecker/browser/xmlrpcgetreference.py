### -*- coding: utf-8 -*- #############################################
"""XMLRPC Edit class to edit any text attributes in vlass

$Id: xmlrpcgetreference.py 49399 2008-01-13 07:24:23Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49399 $"
 
from zope.interface import Interface
from zope.security.proxy import removeSecurityProxy

class XMLRPCGetReference(object) :

    def getReference(self) :
        res = removeSecurityProxy(self.context).values()   
        print res
        return list(res)
        
    __nonzero__ = True
    