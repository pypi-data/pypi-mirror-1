### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: readnotdirectory.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"
 
from zope.interface import Interface,implements
from zope.app.container.interfaces import IReadContainer        
from zope.filerepresentation.interfaces import IReadFile,IReadDirectory
from interfaces import IAttribute, IAttributeDir
from utils import packkey, unpackkey, unpacktype

class ReadNotDirectoryAdapter(object) :

    def __init__(self,context) :
        self.context = context
                
    def __getitem__(self,key) :
        """ A KeyError is raised if there is no value for the key."""
        if key == "++at++" :
            ir = IAttributeDir(self.context)
            return ir
        raise KeyError,key            

    def get(self,key, default=None) :
        """Get a value for a key.  The default is returned if there is no
           value for the key."""
        try :
            return self[key]
        except KeyError :
            return default                           

    def keys(self) :
        """ Return the keys of the mapping object. """
        return ["++at++"]

    def items(self) :
        """ Return the items of the mapping object. """
        return [('++at++',IAttributeDir(self.context))]
        
    def __contains__(self,key) :
        """ Tell if a key exists in the mapping.""" 
        return key == '++at++'

    def __iter__(self) :
        """ Return an iterator for the keys of the mapping object. """
        yield "++at++"            
        
    def values(self) :
        """Return the values of the mapping object."""
        return [ IAttributeDir(self.context) ]

    def __len__(self) :
        return 1

