### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: readdirectory.py 49218 2008-01-06 04:07:07Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49218 $"
 
from zope.interface import Interface,implements
from utils import packkey, unpackkey, unpacktype
from readnotdirectory import ReadNotDirectoryAdapter

class ReadDirectoryAdapter(ReadNotDirectoryAdapter) :
    def __init__(self,context) :
        super(ReadDirectoryAdapter,self).__init__(context)
        
    def __getitem__(self,key) :
        """ A KeyError is raised if there is no value for the key."""
        try :
            return super(ReadDirectoryAdapter,self).__getitem__(key)
        except KeyError :
            return self.context[unicode(unpackkey(key))]

    def keys(self) :
        """ Return the keys of the mapping object. """
        return [ x for x,y in self.items() ] 

    def items(self) :
        """ Return the items of the mapping object. """
        return \
            [ (packkey(x,y),y) for x,y in self.context.items()] \
            + super(ReadDirectoryAdapter,self).items()
        
    def __contains__(self,key) :
        """ Tell if a key exists in the mapping.""" 
        if super(ReadDirectoryAdapter,self).__contains__(key) :
            return True

        key = unpackkey(key)
        return self.context.__contains__(unicode(key)) 

    def __iter__(self) :
        """ Return an iterator for the keys of the mapping object. """
        return iter(self.keys())
        
    def values(self) :
        """Return the values of the mapping object."""
        return \
            list(self.context.value()) \
            + super(ReadDirectoryAdapter,self).values()

    def __len__(self) :
        return self.context.__len__() + super(ReadDirectoryAdapter,self).__len__()

