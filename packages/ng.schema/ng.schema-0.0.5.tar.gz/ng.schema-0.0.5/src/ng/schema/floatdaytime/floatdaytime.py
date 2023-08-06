### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FloatDayTime and InvalidFloatDayTime classes for the Zope 3 based
ng.schema.floatdaytime package

$Id: floatdaytime.py 51938 2008-10-23 08:22:07Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51938 $"

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

    def convertTime(self, strTime) :
        """Convert HH:MM SS time into float value"""
        if type(strTime) in [str,unicode] :
            hms = match(strTime)
            if hms is None :
                raise InvalidFloatDayTime()
            hms = hms.groupdict()
            floatTime = float(int(hms['hour'] or 0) * 60 * 60 + int(hms['minute'] or 0) * 60 + int(hms['second'] or 0))
            return floatTime
        return strTime                    
        

    def __init__(self, min='00:00', max='24:00', missing_value='00:00', *kv, **kw) :
    
        super(FloatDayTime, self).__init__(    min=self.convertTime(min),
                                               max=self.convertTime(max),
                                               missing_value=self.convertTime(max),
                                               *kv, **kw)

    def _validate(self, value) :
        try :
            value = self.convertTime(value)
        except TypeError :
            raise InvalidFloatDayTime()
        
        return super(FloatDayTime, self)._validate(value)

    def set(self, ob, value) :
        super(FloatDayTime, self).set(ob, self.convertTime(value))

    def get(self, ob) :
        d = int(super(FloatDayTime, self).get(ob))
        try :
            value = "%02d:%02d:%02d" % ((d / 60 / 60) % 60, (d / 60) % 60, d % 60)
        except TypeError:
            value = d
        return value
