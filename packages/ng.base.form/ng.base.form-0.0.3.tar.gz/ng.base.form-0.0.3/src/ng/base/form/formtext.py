### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Description for text field of form

$Id: formtext.py 50743 2008-02-19 13:15:02Z antel $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50743 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IFormText
from zope.app.container.interfaces import IContained
from zope.app.container.btree import BTreeContainer
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.schema import Text
from formitembase import FormItemBase
from zope.schema import getFieldNames
from zope.schema.interfaces import IText

class FormText(FormItemBase):
    __doc__ = IFormText.__doc__
    implements(IFormText)

    default = u""
    missing_value = u''

    def factory(self) :
        nf = IFormText(self)
        return Text(**dict([ (x,getattr(nf,x)) for x in getFieldNames(IFormText) if hasattr(self,x) ]))