### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: directoryfactory.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"
 
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IDirectoryFactory
from pd.lib.utility import name2klass
from ng.ftp.utils import packkey, unpackkey, unpacktype

class DirectoryFactory(object) :
    implements(IDirectoryFactory)
    def __init__(self,context) :
        self.context = context
        
    def __call__(self,name) :
        return name2klass(unpacktype(name))()
