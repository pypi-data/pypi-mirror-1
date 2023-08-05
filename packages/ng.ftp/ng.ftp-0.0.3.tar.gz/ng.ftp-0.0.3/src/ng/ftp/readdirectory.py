### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: readdirectory.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"
 
from zope.interface import Interface,implements
from zope.app.container.interfaces import IReadContainer        
from zope.filerepresentation.interfaces import IReadFile,IReadDirectory
from interfaces import IAttribute, IAttributeDir
from utils import packkey, unpackkey, unpacktype

class ReadDirectoryAdapter(object) :

    def __init__(self,context) :
        self.context = context
        
    def __getitem__(self,key) :
        """ A KeyError is raised if there is no value for the key."""
        if key == "++at++" :
            return IAttributeDir(self.context)
        return self.context[unicode(unpackkey(key))]

    def get(self,key, default=None) :
        """Get a value for a key.  The default is returned if there is no
           value for the key."""
        if key == "++at++" :
            return IAttributeDir(self.context)
        return self.context.get(unicode(unpackkey(key)), default=None)

    def keys(self) :
        """ Return the keys of the mapping object. """
        return [ x for x,y in self.items() ] + ["++at++"]

    def items(self) :
        """ Return the items of the mapping object. """
        return [ (packkey(x,y),y) for x,y in self.context.items()] + [('++at++',IAttributeDir(self.context))]
        
    def __contains__(self,key) :
        """ Tell if a key exists in the mapping.""" 
        key = unpackkey(key)
        return self.context.__contains__(unicode(key)) or key == '++at++'

    def __iter__(self) :
        """ Return an iterator for the keys of the mapping object. """
        
        yield "++at++"            
        for key,value in self.context.items() :
            yield packkey(key,value)
        
    def values(self) :
        """Return the values of the mapping object."""
        
        return list(self.context.value()) + [ IAttributeDir(self.context) ]

    def __len__(self) :
        return self.context.__len__() + 1

