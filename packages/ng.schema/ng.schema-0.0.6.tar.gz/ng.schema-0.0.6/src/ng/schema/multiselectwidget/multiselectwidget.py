### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: multiselectwidget.py 52464 2009-02-06 10:04:15Z corbeau $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52464 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy

from zope.app.form.browser.itemswidgets import OrderedMultiSelectWidget

from zope.schema.interfaces import ICollection, IChoice

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class MultiSelectWidget(OrderedMultiSelectWidget) :

    template = ViewPageTemplateFile('multiselectwidget.pt')

    def __init__(self, field, value_type, request) :
        super(MultiSelectWidget, self).__init__(field, value_type, request)
        self.vocabulary = IChoice(value_type).vocabulary

    def getInputValue(self) :
        value = self._toFieldValue(self._getFormInput())
        if value == []:
            return ()
        return super(MultiSelectWidget, self).getInputValue()
