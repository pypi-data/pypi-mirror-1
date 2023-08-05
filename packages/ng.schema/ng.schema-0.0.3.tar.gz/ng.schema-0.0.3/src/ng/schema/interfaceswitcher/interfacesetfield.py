### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InterfaceSet field

$Id: interfacesetfield.py 49317 2008-01-09 19:13:54Z cray $
"""

__author__  = "Andrey Orlov, 2007"
__license__ = "ZPL"
__version__ = "$Revision: 49317 $"

from zope.schema import Set,Choice
from interfaces import IInterfaceSetField
from zope.interface import implements 
from zope.interface import \
    implementedBy, directlyProvidedBy, noLongerProvides, alsoProvides

from zope.security.proxy import removeSecurityProxy
from interfacevocabulary import InterfaceVocabulary
from pd.lib.utility import klass2name
    
class InterfaceSet(Set):
    implements(IInterfaceSetField)
    iface = None
    
    def __init__(self, interface=None, *kv, **kw):
        self.iface = interface
        super(InterfaceSet, self).__init__( 
            value_type=Choice(source=InterfaceVocabulary(self)), 
            *kv, **kw)

    def get(self, object) :
        object = removeSecurityProxy(object)
        values = set()
        for interface in directlyProvidedBy(object) :
            if interface.extends(self.iface) :
                values.add(interface)
        return values                

    def set(self, object, values) :
        print "InterfaceSet", values
        if values == None :
            values = set([])
        object = removeSecurityProxy(object)
        for interface in directlyProvidedBy(object):
            if interface.extends(self.iface) :
                noLongerProvides(object, interface)

        for value in values :                
            alsoProvides(object, value)                

        super(InterfaceSet,self).set(object, 
            set([klass2name(x) for x in values])
            )                         
