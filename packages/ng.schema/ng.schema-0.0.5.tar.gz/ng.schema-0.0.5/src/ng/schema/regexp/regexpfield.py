### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Regexp input field 

$Id: regexpfield.py 51938 2008-10-23 08:22:07Z cray $
"""

__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 51938 $"

from zope.schema import TextLine
from interfaces import IRegexpField
from zope.interface import implements
from zope.schema import ValidationError
import re

class RegexpValidationError(ValidationError) :
    """ Error in regexp matching """
    
    def doc(self) :
        return ",".join(self.args)

class Regexp(TextLine):
    implements(IRegexpField)
    regexp = ()
    rewrite = ()     

    def __init__(self, regexp=(), rewrite=(), *kv, **kw):
        self.regexp = regexp
        self.rewrite = rewrite
        super(Regexp, self).__init__(*kv, **kw)
        
    def set(self,object,value) :
        for reg,rew in self.rewrite :
            res = re.compile(reg,re.U).match(value)
            if res :
                value = rew % res.groupdict()
                
        return super(Regexp,self).set(object,value)                

    def _validate(self,value) :
        ls = []
        try :
            super(Regexp,self)._validate(value)
        except ValidationError,msg :
            if isinstance(msg,tuple) or isinstance(msg,list) :
                ls.extend(msg)
            else :
                ls.append(msg)                            
                        
        for flag,reg,msg in self.regexp :
            if bool(re.compile(reg,re.U).match(value)) <> flag :
                ls.append(msg)

        if ls :                
            raise RegexpValidationError(*ls)
        