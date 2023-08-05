### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: writeattribute.py 49222 2008-01-06 04:47:35Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49222 $"
 
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IWriteFile


class Attribute2WriteFileAdapter(object) :
    implements(IWriteFile)
    
    def __init__(self,context) :
        self.context = context
        
    def write(self,value) :
        self.context.write(value)
        
