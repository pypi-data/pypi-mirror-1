### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: readattributes.py 49316 2008-01-09 16:25:19Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49316 $"
 
import sys
from zope.interface import Interface,implements
from zope.app.container.interfaces import IReadContainer        
from zope.filerepresentation.interfaces import IReadDirectory
from zope.filerepresentation.interfaces import IReadFile
from interfaces import IAttribute, IAttributeDir
from zope.schema.interfaces import IField

class AttributeDir2ReadDirectoryAdapter(dict):
    implements(IReadDirectory)

    def __init__(self,context) :
        self.context = context
        for key,value in self.context.items() :
            if hasattr(self.context.context,key) :
                self[key] = value
                        
class AttributeDirBase(dict) :
    __name__ = "++at++"
    ifaces = []
    implements(IAttributeDir,IReadContainer)
    
    def __init__(self,context) :
        self.context = context    
        for iface in self.ifaces :
            for name in iface.names(all=True) :
                if name not in self and self.filter(name):
                    if IField.providedBy(iface[name]) :
                        self[name] = iface[name].bind(self.context)

    def filter(self,name) :
        return True
        return hasattr(self.context,name)
