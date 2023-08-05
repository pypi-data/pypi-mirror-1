### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: writedirectory.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"
 
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IWriteFile,IWriteDirectory
from utils import packkey, unpackkey, unpacktype

class WriteDirectoryAdapter(object) :
    implements(IWriteDirectory)

    def __init__(self,context) :
        self.context = context
        
    def __setitem__(self,key,value) :
        """ A KeyError is raised if there is no value for the key."""
        self.context[unicode(unpackkey(key))] = value       

    def __delitem__(self,key,value) :
        del self.context[unicode(unpackkey(key))] 
