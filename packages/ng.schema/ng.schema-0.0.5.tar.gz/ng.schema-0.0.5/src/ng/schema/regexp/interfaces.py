### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Inrefaces for the Zope 3 based smartimagecache package

$Id: interfaces.py 51938 2008-10-23 08:22:07Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 51938 $"
__date__ = "$Date: 2008-10-23 12:22:07 +0400 (Чтв, 23 Окт 2008) $"

from zope.schema.interfaces import ITextLine
from zope.schema import TextLine, Tuple, Field
from zope.interface import Interface

class IRegexpField(ITextLine):
    """Regexp Text Line Field"""

    regexp = Field()

    rewrite = Field()    