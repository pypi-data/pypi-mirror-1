### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InterfaceSet field

$Id: interfacesetfield.py 51938 2008-10-23 08:22:07Z cray $
"""

__author__  = "Andrey Orlov, 2007"
__license__ = "ZPL"
__version__ = "$Revision: 51938 $"

from zope.schema import Set,Choice
from interfaces import IInterfaceSetField
from zope.interface import implements 
from zope.interface import \
    implementedBy, directlyProvidedBy, noLongerProvides, alsoProvides

from zope.security.proxy import removeSecurityProxy
from interfacevocabulary import InterfaceVocabulary, InterfaceTitledVocabulary
from pd.lib.utility import klass2name
    
class InterfaceSet(Set):
    implements(IInterfaceSetField)
    iface = None
    
    def __init__(self, interface=None, with_title=True, *kv, **kw):
        self.iface = interface
        super(InterfaceSet, self).__init__( 
            value_type=with_title and Choice(source=InterfaceTitledVocabulary(self)) or Choice(source=InterfaceVocabulary(self)), 
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
