### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Inrefaces for the Zope 3 based ng.widget.interface package

$Id: interfaces.py 51938 2008-10-23 08:22:07Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 51938 $"

from zope.schema.interfaces import IChoice, ISet
from zope.schema import TextLine
from zope.interface import Interface
from zope.configuration.fields import GlobalInterface, Bool

class IInterfaceChoiceField(IChoice):
    """Interface choice Field"""

    iface = GlobalInterface()

    with_title = Bool()

class IInterfaceSetField(ISet):
    """Interface setField"""

    iface = GlobalInterface()
    
    with_title = Bool()