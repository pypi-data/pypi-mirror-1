### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.pager package

$Id: interfaces.py 13308 2007-11-27 11:54:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 13308 $"

from zope.interface import Interface
from zope.filerepresentation.interfaces import IReadFile, IWriteFile

class IAttribute(Interface):
    pass

class IAttributeDir(Interface):
    pass

