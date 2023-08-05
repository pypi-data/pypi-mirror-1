### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: nsat.py 49254 2008-01-07 23:58:46Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49254 $"

from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import SimpleHandler
from interfaces import IAttributeDir
from zope.security.proxy import removeSecurityProxy

class NsAt(SimpleHandler):
    """ ++at++"""
    implements(ITraversable)

    def traverse(self,name,ignored) :
        return IAttributeDir(self.context)
        
        