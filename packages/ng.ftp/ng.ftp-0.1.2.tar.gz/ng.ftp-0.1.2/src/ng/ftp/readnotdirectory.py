### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: readnotdirectory.py 49255 2008-01-08 00:13:43Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49255 $"
 
from zope.interface import Interface,implements
from interfaces import IAttributeDir
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from zope.filerepresentation.interfaces import IReadDirectory

class ReadNotDirectoryAdapter(object) :
    implements(IReadDirectory)

    def __init__(self,context) :
        self.context = context
                
    def __getitem__(self,key) :
        """ A KeyError is raised if there is no value for the key."""
        try :
            if key == "++at++" :
                return IAttributeDir(self.context)
            elif key == "++annotations++" :
                return removeSecurityProxy(IAnnotations(self.context))            
        except TypeError :
            pass
                            
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
        return [ x for x,y in self.items() ]

    def items(self) :
        """ Return the items of the mapping object. """

        return [(x,y) for x,y in
             ('++at++', IAttributeDir(self.context,None)), 
             ('++annotations++', IAnnotations(self.context,None)) if y is not None ]
        
    def __contains__(self,key) :
        """ Tell if a key exists in the mapping.""" 
        try :
            self[key]
            return True
        except KeyError :
            return False            

    def __iter__(self) :
        """ Return an iterator for the keys of the mapping object. """
        return iter(self.keys())
        
    def values(self) :
        """Return the values of the mapping object."""
        return [ y for x,y in self.items() ]

    def __len__(self) :
        return len(self.keys())
