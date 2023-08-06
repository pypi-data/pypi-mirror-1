### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for dialog form 

$Id: formedit.py 53587 2009-08-13 17:48:25Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 53587 $"

from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.interface import implements,implementedBy
from zope.security.proxy import removeSecurityProxy
from zope.schema import getFieldsInOrder, getFieldNamesInOrder
from ng.base.form.interfaces import IFormSave
from ng.base.form.interfaces import IForm

class FormEdit(object) :
    complete = False
    def __init__(self,context,request) :
        self.schema = InterfaceClass('IGeneredForm',(Interface,), 
            dict([ (x,removeSecurityProxy(y.factory())) for x,y in context.items()  ])
        )
        self.fieldNames = context.keys()
        super(FormEdit,self).__init__(context,request)
        self.label = IForm(context).label
        self.okmessage = IForm(context).okmessage
        
    def getData(self,*kv,**kw) :
        return dict( [ (name,x.default) for name,x in self.context.items() ] )
        
    def setData(self,d,**kw) :
        IFormSave( self.context ).do( d )
        self.complete = True
        return self.okmessage
                    