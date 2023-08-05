### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: nsannotations4object.py 49258 2008-01-08 01:29:00Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49258 $"

from zope.interface import implements
from ng.ftp.nsat import NsAt
from zope.filerepresentation.interfaces import IReadDirectory
from zope.annotation.interfaces import IAnnotations
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import SimpleHandler
from zope.security.proxy import removeSecurityProxy

import sys

class NsAnnotations4Object(SimpleHandler) :
    """ ++annotations++ object """

    implements(ITraversable)

    def traverse(self,name,ignored) :
        try :
            return IAnnotations(removeSecurityProxy(IReadDirectory(self.context).context))
        except :
            print sys.excepthook(*sys.exc_info())
            raise   
        