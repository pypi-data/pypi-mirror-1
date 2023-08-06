### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Container for form items 

$Id: formcontainer.py 53587 2009-08-13 17:48:25Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53587 $"

from zope.interface import implements
from interfaces import IFormContainer
from zope.app.container.ordered import OrderedContainer,IOrderedContainer

class Form( OrderedContainer ):
    implements(IFormContainer,IOrderedContainer)

    label = u"Edit something"

    okmessage = u""    