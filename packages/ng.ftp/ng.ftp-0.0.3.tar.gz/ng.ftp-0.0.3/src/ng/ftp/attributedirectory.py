### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: attributedirectory.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"
 
import sys
from zope.interface import Interface,implements
from zope.app.container.interfaces import IReadContainer        
from zope.filerepresentation.interfaces import IReadDirectory
from zope.filerepresentation.interfaces import IReadFile
from interfaces import IAttribute, IAttributeDir
from zope.schema.interfaces import IField

class AttributeWrapper(object) :
    implements(IAttribute)
    def __init__(self,context,field) :
        self.context = context
        self.field = field

    def read(self) :
        return str(self.field.get(self.context.context.context))
        
        return str(getattr(
            self.context.context.context,
            self.attribute,
            None))

    def write(self,value) :
        return self.field.set(self.context.context.context,value)
        
        return setattr(
            self.context.context.context,
            self.attribute,
            value)

class AttributeDir2ReadDirectoryAdapter(dict):
    implements(IReadDirectory)

    def __init__(self,context) :
        self.context = context
        for iface in self.context.ifaces :
            for name in iface.names(all=True) :
                if name not in self :
                    if IField.providedBy(iface[name]) :
                        self[name] = iface[name].bind(self.context.context)
                        
class AttributeDirBase(object) :
    __name__ = "++at++"
    ifaces = []
    implements(IAttributeDir,IReadContainer)
    
    def __init__(self,context) :
        self.context = context    

