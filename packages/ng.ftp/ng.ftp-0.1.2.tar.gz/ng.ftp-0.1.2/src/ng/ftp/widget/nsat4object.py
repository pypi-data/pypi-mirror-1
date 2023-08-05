### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: nsat4object.py 49258 2008-01-08 01:29:00Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49258 $"

from ng.ftp.nsat import NsAt
from zope.filerepresentation.interfaces import IReadDirectory
from ng.ftp.interfaces import IAttributeDir
import sys

class NsAt4Object(NsAt) :
    """ ++at++ object """
    
    def traverse(self,name,ignored) :
        try :
            return IAttributeDir(IReadDirectory(self.context).context)
        except :
            print sys.excepthook(*sys.exc_info())
            raise   
