### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FloatDayTime class for the Zope 3 based ng.schema.floatdaytime package

$Id: floatdaytime.py 49075 2007-12-29 12:14:46Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49075 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.schema import Float
from zope.schema.interfaces import ValidationError

import time
import re

match = re.compile("^((?P<hour>[0-9]+):(?P<minute>[0-9]+))?:?((?P<second>[0-9]+))?$").match

class InvalidFloatDayTime(ValidationError) :
    __doc__ = u"""Value must have HH:MM:SS format"""

class FloatDayTime(Float) :

    def _validate(self, value) :
        if not match(value) :
            raise InvalidFloatDayTime()

    def set(self, ob, value) :
        d = match(value).groupdict()
        super(FloatDayTime, self).set(ob, 
            int(d['hour'] or 0) * 60 * 60 + int(d['minute'] or 0) * 60 + int(d['second'] or 0)
        )
    
    def get(self, ob) :
        d = super(FloatDayTime, self).get(ob)
        value = "%02d:%02d:%02d" % ((d / 60 / 60) % 60, (d / 60) % 60, d % 60)
        return value
