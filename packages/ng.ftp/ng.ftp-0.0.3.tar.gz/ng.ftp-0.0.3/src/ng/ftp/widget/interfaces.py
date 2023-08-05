### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.pager package

$Id: interfaces.py 13543 2007-12-10 00:52:49Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 13543 $"

from zope.interface import Interface
from zope.schema import Field, Tuple, Int, Bool
from zope.filerepresentation.interfaces import IReadFile, IWriteFile


class IReadWriteFile(IReadFile, IWriteFile) :
    """ """
    pass

