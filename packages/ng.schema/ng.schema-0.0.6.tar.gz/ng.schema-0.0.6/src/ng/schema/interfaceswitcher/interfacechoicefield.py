### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InterfaceSwitcher field

$Id: interfacechoicefield.py 51928 2008-10-22 21:22:45Z cray $
"""

__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 51928 $"

from zope.schema import Choice
from interfaces import IInterfaceChoiceField
from zope.interface import implements 
from zope.app.zapi import getUtilitiesFor
from zope.interface.interfaces import IInterface
from zope.interface import \
    implementedBy, directlyProvidedBy, noLongerProvides, alsoProvides
from zope.security.proxy import removeSecurityProxy
from interfacevocabulary import InterfaceVocabulary, InterfaceTitledVocabulary
from pd.lib.utility import klass2name
    
class InterfaceChoice(Choice):
    implements(IInterfaceChoiceField)
    iface = None
    
    def __init__(self, interface=None, with_title=True, *kv, **kw):
        self.iface = interface
        super(InterfaceChoice, self).__init__( 
            source=with_title and InterfaceTitledVocabulary(self) or InterfaceVocabulary(self), 
            *kv, **kw)

    def get(self, object) :
        object = removeSecurityProxy(object)
        for interface in directlyProvidedBy(object) :
            if interface.extends(self.iface) :
                return interface

    def set(self, object, value) :
        object = removeSecurityProxy(object)
        for interface in directlyProvidedBy(object):
            if interface.extends(self.iface) :
                noLongerProvides(object, interface)
        alsoProvides(object, value)                
        super(InterfaceChoice,self).set(object, klass2name(value))                         
