### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: ftpinterfacewidget.py 49315 2008-01-09 16:06:50Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49315 $"

from zope.interface import implements
from zope.component import adapts
from ftpwidget import FtpWidgetBase
from pd.lib.utility import name2klass, klass2name
from ng.schema.interfaceswitcher.interfaces import IInterfaceChoiceField, IInterfaceSetField

class InterfaceChoiceWidget(FtpWidgetBase) :
    adapts(IInterfaceChoiceField)

    def convertor(self,value) :
        return name2klass(value)
        
    def serialize(self,value) :
        return klass2name(value)

class InterfaceSetWidget(FtpWidgetBase) :
    adapts(IInterfaceSetField)

    def convertor(self,values) :
        if not values :
            return set([]) 
        return set( [ name2klass(value)  for value in eval(values) ] )
        
    def serialize(self,values) :
        return str([ klass2name(value) for value in values ])
