### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: ftpobjectwidget.py 49258 2008-01-08 01:29:00Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49258 $"

from zope.interface import implements
from zope.component import adapts
from zope.schema.interfaces import IField, IObject
from zope.security.proxy import removeSecurityProxy
from ng.ftp.readnotdirectory import ReadNotDirectoryAdapter
import sys

class ObjectWidget(ReadNotDirectoryAdapter) :
    adapts(IObject)
    
    def __init__(self,field) :
        self.field = field
        super(ObjectWidget,self).__init__(field.get(removeSecurityProxy(self.field).context))
        
        


