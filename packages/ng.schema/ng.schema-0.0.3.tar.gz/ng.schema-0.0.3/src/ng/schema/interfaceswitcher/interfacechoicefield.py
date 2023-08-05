### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InterfaceSwitcher field

$Id: interfacechoicefield.py 49300 2008-01-08 21:35:18Z cray $
"""

__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 49300 $"

from zope.schema import Choice
from interfaces import IInterfaceChoiceField
from zope.interface import implements 
from zope.app.zapi import getUtilitiesFor
from zope.interface.interfaces import IInterface
from zope.interface import \
    implementedBy, directlyProvidedBy, noLongerProvides, alsoProvides
from zope.security.proxy import removeSecurityProxy
from interfacevocabulary import InterfaceVocabulary
from pd.lib.utility import klass2name
    
class InterfaceChoice(Choice):
    implements(IInterfaceChoiceField)
    iface = None
    
    def __init__(self, interface=None, *kv, **kw):
        self.iface = interface
        super(InterfaceChoice, self).__init__( 
            source=InterfaceVocabulary(self), 
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
