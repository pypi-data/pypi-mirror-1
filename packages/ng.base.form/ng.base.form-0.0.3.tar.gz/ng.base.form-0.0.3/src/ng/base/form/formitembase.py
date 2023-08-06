### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class to implement different form items 

$Id: formitembase.py 53587 2009-08-13 17:48:25Z cray $
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
from zope.schema import Field


class FormItemBase(Persistent,Contained) :
    """ Base class for the fields - items of the form container """
    implements(IFormContent) 
    
    title = ""
    factory = Field 
    data = ""
