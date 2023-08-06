# -*- coding: utf-8 -*-
"""The dialog namespace adapter.

$Id: dialognamespace.py 53261 2009-06-12 10:41:11Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53261 $"

from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.component.interface import nameToInterface
from zope.traversing.namespace import SimpleHandler
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.location import location
from zope.app.zapi import getUtility, getMultiAdapter
from ng.base.form.interfaces import IFormDialog

class DialogNamespace(SimpleHandler):
    """ ++dialog++ """

    implements(ITraversable)

    def __init__(self, context, request):
        super(DialogNamespace,self).__init__(context)
        self.request = request

    def traverse(self,name,ignored) :
        """ Алгоритм вытягивания диалога от утилиты IDialog """

        return getMultiAdapter(
            (
                location.LocationProxy(
                    getUtility(IFormDialog,context=self.context,name=name), 
                    self.context, 
                    ""
                ),
                self.request
            ),
            name='dialog.html'
        )

