### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Decription for int field of form

$Id: formint.py 53587 2009-08-13 17:48:25Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53587 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IForm,IFormInt,IFormContent,IFormContainer,IFormTextLine
from zope.app.container.interfaces import IContained
from zope.app.container.btree import BTreeContainer
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.schema import TextLine, Int
from formitembase import FormItemBase
from zope.schema import getFieldNames

class FormInt(FormItemBase):
    __doc__ = IFormInt.__doc__
    implements(IFormInt)

    default = 0
    missing_value = 0
    title = u''
    min = -1000
    max = 1000

    def factory(self) :
        nf = IFormInt(self)
        return Int(**dict([ (x,getattr(nf,x)) for x in getFieldNames(IFormInt) if hasattr(self,x) ]))
