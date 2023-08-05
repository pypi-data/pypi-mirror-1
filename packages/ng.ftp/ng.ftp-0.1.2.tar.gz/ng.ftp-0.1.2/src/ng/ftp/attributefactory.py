### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: attributefactory.py 49344 2008-01-11 07:30:09Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49344 $"
 
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IDirectoryFactory, IFileFactory
from pd.lib.utility import name2klass
from ng.ftp.utils import packkey, unpackkey, unpacktype

class AttributeFactory(object) :
    implements(IDirectoryFactory)
    def __init__(self,context) :
        self.context = context
        return
        
    def __call__(self,name,content_type="text/plain",data=None) :
        print "Create FILE:",content_type, data
        return data
        
        
