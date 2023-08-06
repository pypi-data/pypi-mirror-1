### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InterfaceSwitcher field

$Id: interfacevocabulary.py 51938 2008-10-23 08:22:07Z cray $
"""

__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 51938 $"

from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
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
    
class InterfaceTitledVocabulary(InterfaceVocabulary) :

    def __call__(self, object) :        
        return SimpleVocabulary(
            sorted(
                [SimpleTerm(interface, name, interface.__doc__) 
                    for (name,interface) in getUtilitiesFor(IInterface, object)
                    if interface.extends(self.ob.iface)],
                key = lambda x : x.token)
            )


