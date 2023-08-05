### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.pager package

$Id: interfaces.py 49222 2008-01-06 04:47:35Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49222 $"

from zope.interface import Interface
from zope.filerepresentation.interfaces import IReadFile, IWriteFile

class IAttribute(Interface):
    pass

class IAttributeDir(Interface):
    pass

