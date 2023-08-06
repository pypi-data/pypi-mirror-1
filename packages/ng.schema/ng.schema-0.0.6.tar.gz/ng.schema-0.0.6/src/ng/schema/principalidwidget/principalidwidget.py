### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: principalidwidget.py 51928 2008-10-22 21:22:45Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51928 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy

from zope.app.form.browser.textwidgets import TextWidget
from zope.app.form.browser.interfaces import ITextBrowserWidget
from zope.app.form.browser.widget import renderElement

class PrincipalIdWidget(TextWidget) :

    def __call__(self) :
        return renderElement(
                   self.tag,
                   type=self.type,
                   name=self.name,
                   readonly=True,
                   id=self.name,
                   value=self._getFormValue(),
                   cssClass=self.cssClass,
                   extra=self.extra
               )
    
    def _getFormValue(self) :
        return getattr(self.request.principal, 'title', getattr(self.request.principal, 'id', u'Anonymous' ))
    
    def getInputValue(self) :

        value = getattr(self.request.principal, 'id', u'Anonymous')

        return value
