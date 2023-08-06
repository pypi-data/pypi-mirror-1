### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based base form package

$Id: interfaces.py 53587 2009-08-13 17:48:25Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53587 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Int, Choice, Tuple
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema.interfaces import ITextLine, IInt, IText
from ng.schema.regexp.interfaces import IRegexpField
from zope.schema import Object

class IFormTextLine(ITextLine):
    u"""Field containing a unicode string without newlines."""
    default = TextLine(
            title = u'Value of textual parameter',
            description = u'',
            default = u'',
            required = False)
            
    missing_value = TextLine(
            title = u'Value of textual parameter',
            description = u'',
            default = u'',
            required = False)

class IFormInt(IInt):
    u"""Field containing an Integer Value."""

    default = Int(
        title = u'Value of int parameter',
        description = u'',
        default = 0,
        required = False)

    missing_value = Int(
        title = u'Value of int parameter',
        description = u'',
        default = 0,
        required = False)

class IFormText(IText):
    u"""Field containing a unicode string without newlines."""
    default = Text(
            title = u'Value of textual parameter',
            description = u'',
            default = u'',
            required = False)
            
    missing_value = TextLine(
            title = u'Value of textual parameter',
            description = u'',
            default = u'',
            required = False)

class IFormRegexpRegexp (Interface) :
    u""" """
    flag = Bool(
        title=u'flag',
        description=u'',
        default=False
        )
      
    reg = TextLine(
                       title = u'reg',
                       description = u'reg',
                       default = u'',
                       required = False)

    msg = TextLine(
                       title = u'msg',
                       description = u'msg',
                       default = u'',
                       required = False)

class IFormRegexpRewrite (Interface) :
    u""" """
    reg = TextLine(
                   title = u'reg',
                   description = u'reg',
                   default = u'',
                   required = False)

    rew = TextLine(
                   title = u'rew',
                   description = u'rew',
                   default = u'',
                   required = False)

class IFormRegexp(IRegexpField):
    u""" """
    default = TextLine(
            title = u'Value of textual parameter',
            description = u'',
            default = u'',
            required = False)

    regexp = Tuple(title=u'regexp',
                    description=u'regexp',
                    required=False,
                    value_type=Object(title=(u'regexp'),
                                      description=(u'...'),
                                      schema=IFormRegexpRegexp,
                                     )
                   )

    rewrite = Tuple(title=u'rewrite',
                    description=u'rewrite',
                    required=False,
                    value_type=Object(title=(u'rewrit'),
                                      description=(u'...'),
                                      schema=IFormRegexpRewrite,
                                     )
                   )

class IForm(Interface):
    """A form definitions """

    label = TextLine(
        title = u'Form title',
        description = u'',
        default = u'Edit something',
        required = False)

    okmessage = Text(
        title = u'Ok-message',
        description = u'',
        default = u'',
        required = False)
            
class IFormContent(Interface):
    """ Iterface that specify permission of object that can be content
        of registry """

    factory = Field(title=u"Factory used to create form field")

    __parent__ = Field(constraint = ContainerTypesConstraint(IForm))
    
class IFormContainer(IContainer, IForm):
    """Registry Container"""

    def __setitem__(name, object):
        pass

    __setitem__.precondition = ItemTypePrecondition(IFormContent)

class IFormDialog(IForm) :
    """Interface of dialogable component"""

class IFormSave(Interface):
    """ """
    def do(self,d,**kw) :
        pass