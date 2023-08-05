### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: writedirectory.py 49218 2008-01-06 04:07:07Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49218 $"
 
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IWriteFile,IWriteDirectory
from utils import packkey, unpackkey, unpacktype
import sys

class WriteDirectoryAdapter(object) :
    implements(IWriteDirectory)

    def __init__(self,context) :
        self.context = context
        
    def __setitem__(self,key,value) :
        """ A KeyError is raised if there is no value for the key."""
        try :
            self.context[unicode(unpackkey(key))] = value       
        except Exception,msg :
            print sys.excepthook(*sys.exc_info())                        
        
    def __delitem__(self,key,value) :
        del self.context[unicode(unpackkey(key))] 
