### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Inrefaces for the Zope 3 based smartimagecache package

$Id: interfaces.py 13308 2007-11-06 21:14:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 13308 $"
__date__ = "$Date: 2007-11-07 00:14:39 +0300 (Срд, 07 Ноя 2007) $"

from zope.schema.interfaces import ITextLine
from zope.schema import TextLine, Tuple, Field
from zope.interface import Interface

class IRegexpField(ITextLine):
    """Regexp Text Line Field"""

    regexp = Field()

    rewrite = Field()    