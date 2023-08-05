### -*- coding: utf-8 -*- #############################################
"""Adapter of division to attribute dir component.

$Id: attributediradapter.py 49313 2008-01-09 13:47:57Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49313 $"


from ng.ftp.readattributes import AttributeDirBase
from zope.interface import Interface,implements,providedBy
from ng.ftp.interfaces import IAttributeDir

class AttributeDirAdapter(AttributeDirBase) :
    __doc__ = __doc__
    implements(IAttributeDir)
    
    @property
    def ifaces(self) :
        return list(providedBy(self.context))

    def filter(self,name) :
        return name[0] != "_" and super(AttributeDirAdapter,self).filter(name)
                
