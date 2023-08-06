### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class to form view of ng.base.form

$Id: formsave.py 50744 2008-02-19 14:24:50Z antel $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50744 $"

from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.interface import implements,implementedBy
from zope.security.proxy import removeSecurityProxy
from zope.schema import getFieldsInOrder, getFieldNames
from ng.base.form.interfaces import IFormSave

class FormSave(object) :

    def __init__(self,context):
        self.context = context

    def do(self,d,**kw) :
        for key,value in d.items() :
            self.context[key].default = value
        return True
