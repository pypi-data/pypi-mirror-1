### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Decription for regexp field of form

$Id: formregexp.py 50745 2008-02-19 14:34:41Z antel $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50745 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IFormRegexp,IFormRegexpRewrite,IFormRegexpRegexp
from zope.app.container.interfaces import IContained
from zope.app.container.btree import BTreeContainer
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.schema import TextLine, Int
from formitembase import FormItemBase
from zope.schema import getFieldNames
from ng.schema.regexp.regexpfield import Regexp
from zope.schema import Tuple
from ng.schema.regexp.interfaces import IRegexpField
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget

class FormRegexp(FormItemBase):
    __doc__ = IFormRegexp.__doc__
    implements(IFormRegexp)

    def __init__(self,*kv,**kw) :
        super(FormRegexp,self).__init__(*kv,**kw)
        self.regexp = ()
        self.rewrite = ()

    regexp = None
    rewrite = None 
    default = u''

    def factory(self) :
        nf = IFormRegexp(self)
        return Regexp(**dict([ (x,getattr(nf,x)) for x in getFieldNames(IRegexpField) if hasattr(self,x) ]))

class FormRegexpRegexp( Persistent ) :

    implements(IFormRegexpRegexp)

    flag = False

    reg = u''

    msg = u''

class FormRegexpRewrite( Persistent ) :

    implements(IFormRegexpRewrite)

    reg = u''

    rew = u''

FormRegexpRegexpTupleWidget = CustomWidgetFactory(
       TupleSequenceWidget,
       subwidget=CustomWidgetFactory(
       ObjectWidget,
       FormRegexpRegexp))

FormRegexpRewriteTupleWidget = CustomWidgetFactory(
       TupleSequenceWidget,
       subwidget=CustomWidgetFactory(
       ObjectWidget,
       FormRegexpRewrite))
