### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: readannotations.py 49258 2008-01-08 01:29:00Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49258 $"
 
from zope.interface import Interface,implements, alsoProvides
from zope.app.container.interfaces import IReadContainer        
from zope.app.container.interfaces import IContained
from zope.filerepresentation.interfaces import IReadFile,IReadDirectory
from interfaces import IAttribute, IAttributeDir
from utils import packkey, unpackkey, unpacktype
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from zope.location.location import LocationProxy
from zope.app.container.contained import ContainedProxy

class ReadAnnotationsAdapter(object) :

    def __init__(self,context) :
        self.context = context
        
    def __getitem__(self,key) :
        """ A KeyError is raised if there is no value for the key."""
        res = self.get(key)
        if res is not None :
            return res
        raise KeyError            

    def get(self,key, default=None) :
        """Get a value for a key.  The default is returned if there is no
           value for the key."""
        res = self.context.get(unicode(unpackkey(key)), default=None)
        if res and not IContained.providedBy(res) :
            res = ContainedProxy(res)
        return res            

    def keys(self) :
        """ Return the keys of the mapping object. """
        return [ packkey(x,y) for x,y in self.items() ] 

    def items(self) :
        """ Return the items of the mapping object. """
        l = []
        for key,value in [ (packkey(x,y),ContainedProxy(y)) for x,y in self.context.items()] :
            l.append((key,value))
        return l            
        
    def __contains__(self,key) :
        """ Tell if a key exists in the mapping.""" 
        key = unpackkey(key)
        return self.context.has_key(unicode(key)) 

    def __iter__(self) :
        """ Return an iterator for the keys of the mapping object. """
        for key,value in self.items() :
            yield key
        
    def values(self) :
        """Return the values of the mapping object."""
        return [ y for x,y in self.items() ]

    def __len__(self) :
        return len( self.context.keys() )

