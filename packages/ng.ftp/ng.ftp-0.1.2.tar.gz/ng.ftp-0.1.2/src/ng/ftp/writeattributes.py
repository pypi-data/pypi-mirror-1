### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Container adapters the Zope 3 based ftp package

$Id: writeattributes.py 49316 2008-01-09 16:25:19Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49316 $"
 
import sys
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IWriteDirectory
from interfaces import IAttribute, IAttributeDir
from zope.schema.interfaces import IField
from zope.filerepresentation.interfaces import IWriteFile

class AttributeDir2WriteDirectoryAdapter(object) :
    implements(IWriteDirectory)

    def __init__(self,context) :
        self.context = context
        self.__dict = context
        
    def __setitem__(self,key,value) :
        """ A KeyError is raised if there is no value for the key."""
        print "VALUE!!",value
        try :
            IWriteFile(self.__dict[key]).write(value)        
            #self.__dict[key].bind(self.context.context).set(self.context.context,value)
        except Exception,msg :
            print "SETATTR", sys.excepthook(*sys.exc_info())                        
        
    def __delitem__(self,key,value) :
        delattr(self.context.context,key)
                        
