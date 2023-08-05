### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: utils.py 13538 2007-12-09 23:12:17Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13538 $"

from pd.lib.utility import klass2name

def packkey(key,value) :
    return "=".join((key,klass2name(value.__class__)))
    
def unpackkey(key) :
    return key[0:key.rindex("=")]
    
def unpacktype(key) :
    return key[key.rindex("=")+1:]
    