### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InterfaceSwitcher field

$Id: interfacevocabulary.py 49056 2007-12-27 23:17:08Z cray $
"""

__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 49056 $"

from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import  IContextSourceBinder
from zope.app.zapi import getUtilitiesFor

    
class InterfaceVocabulary(object) :
    implements(IContextSourceBinder)

    def __init__(self,ob) :
        self.ob = ob

    def __call__(self, object) :        
        return SimpleVocabulary.fromItems(
            sorted(
                [(name, interface) 
                    for (name,interface) in getUtilitiesFor(IInterface, object)
                    if interface.extends(self.ob.iface)],
                key = lambda (name, interface): name)
            )
