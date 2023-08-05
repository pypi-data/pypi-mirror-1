### -*- coding: utf-8 -*- #############################################
"""Container adapters the Zope 3 based contentobjects package

$Id: ftpwidget.py 49359 2008-01-11 21:15:19Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49359 $"

from zope.interface import implements
from zope.component import adapts
from interfaces import IReadWriteFile
from zope.schema.interfaces import IField, IBool, IBytes, IText, IDate, IDatetime, IFloat, IInt
import datetime
import zope.datetime
from time import strptime
from zope.security.proxy import removeSecurityProxy
import sys

class FtpWidgetBase(object) :
    implements(IReadWriteFile)

    def __init__(self,field) :
        self.field = field

    @property
    def context(self) :
        return removeSecurityProxy(self.field).context

    def convertor(self,value) :
        try :
            return eval(value)
        except SyntaxError,msg :
            print "FIXME:",self,msg,value
            return value            

    def serialize(self,value) :
        return repr(value)        
        
    def write(self,value) :
        self.field.set(self.context,self.convertor(value))
        
    def read(self) :
        try :
            return self.serialize(self.field.get(self.context))
        except Exception, msg:
            print sys.excepthook(*sys.exc_info())
        
    def size(self) :
        return len(self.read())                
        
class FieldWidget(FtpWidgetBase) :
    adapts(IField)

class TextWidget(FtpWidgetBase) :
    adapts(IText)

    def convertor(self,value) :
        return unicode(value)
        
    def serialize(self,value) :
        return str(value)
    
class BytesWidget(FtpWidgetBase) :
    adapts(IBytes)

    def convertor(self,value) :
        return value
        
    def serialize(self,value) :
        return value


class DateTimeWidget(FtpWidgetBase) :
    adapts(IDatetime)
    fmt = "%Y-%m-%d %M:%H:%S"
    len = 19

    def convertor(self,value) :
        try :
            tz = int(value[self.len:])
        except ValueError :
            tz = 0
        return datetime.datetime(*(strptime(value[0:self.len],self.fmt)[0:-2]+(zope.datetime.tzinfo(0),) ))
        
    def serialize(self,value) :
        try :
            return value.strftime(self.fmt+" %z")
        except AttributeError :
            return ""            
        
class DateWidget(DateTimeWidget) :
    adapts(IDate)
    fmt = "%Y-%m-%d"

