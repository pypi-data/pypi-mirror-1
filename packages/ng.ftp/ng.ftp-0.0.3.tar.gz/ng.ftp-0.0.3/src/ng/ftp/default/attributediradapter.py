### -*- coding: utf-8 -*- #############################################
"""Adapter of division to attribute dir component.

$Id: attributediradapter.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"


from ng.ftp.attributedirectory import AttributeDirBase
from zope.interface import Interface,implements,providedBy
from ng.ftp.interfaces import IAttributeDir

class AttributeDirAdapter(AttributeDirBase) :
    __doc__ = __doc__
    implements(IAttributeDir)
    
    @property
    def ifaces(self) :
        return list(providedBy(self.context))
    
    
