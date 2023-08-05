### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Inrefaces for the Zope 3 based ng.widget.interface package

$Id: interfaces.py 13201 2007-11-20 07:50:23Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 13201 $"

from zope.schema.interfaces import IChoice, ISet
from zope.schema import TextLine
from zope.interface import Interface
from zope.configuration.fields import GlobalInterface

class IInterfaceChoiceField(IChoice):
    """Interface choice Field"""

    iface = GlobalInterface()

class IInterfaceSetField(ISet):
    """Interface setField"""

    iface = GlobalInterface()
    