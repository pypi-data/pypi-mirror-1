### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-In class for dialog page

$Id: dialog.py 53587 2009-08-13 17:48:25Z cray $
"""
__author__  = "Andrey Orlov,2009"
__license__ = "GPL"
__version__ = "$Revision: 53587 $"

from formedit import FormEdit
from zope.app.form.utility import setUpDisplayWidgets

class Dialog(FormEdit) :

    def display(self) :
        return u""

    def setData(self,d,**kw) :
        for name in self.fieldNames :
            delattr(self,name + '_widget')
        
        setUpDisplayWidgets(self, self.schema, source=type('schemasource',(object,),d), names=self.fieldNames)


        return super(Dialog,self).setData(d,**kw)
    