### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: nsat.py 49222 2008-01-06 04:47:35Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49222 $"

from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.component.interface import nameToInterface
from zope.traversing.namespace import SimpleHandler
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.location import location
from interfaces import IAttributeDir

class NsAt(SimpleHandler):
    """ ++at++"""
    implements(ITraversable)

    def __init__(self,*kv,**kw) :
        super(NsAt,self).__init__(*kv,**kw)

    def traverse(self,name,ignored) :
        return IAttributeDir(self.context)
        
