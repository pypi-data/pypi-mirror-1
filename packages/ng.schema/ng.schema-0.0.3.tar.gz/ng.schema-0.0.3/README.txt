The ng.schema product
=====================


The ng.schema is zope3 product developed to provide some interface (schema)
fields and widget. Current field and widget list are:

    interfaceswitcher
        Field can be used to dynamic switch subinterfaces of
        some interface;
      
        Sample of use ::
        
            class IA(Interface) :
                pass
                
            class IA1(IA) :
                pass
                
            class IA2(IA) :
                pass
                
            class IOb(Interface) :
            
                interface = InterfaceSwitcher(
                    title=u'Interface of IA',
                    interface = IA,
                    )

    regexp
        Product can be used to check input text line with some set of
        regexp and customize text line with some rewrite rules before set.
        
        Sample of use ::
        
            class IOb(Interface) :
            
                title = Regexp(title = u'Title',
                    description = u'Title',
                    default = u'',
                    required = True,
                    regexp = (
                          (False, u"^.*/.*$", u"Title do not content symbol '/'"),
                        ),
                    rewrite = (
                        (u"^\s*(?P<name>\w+)\s*-\s*?(?P<number>[0-9]+)\s*$", u"%(name)s-%(number)s"),
                        (u"^\s*(?P<name>[^\s])\s*$", u"%(name)s"),
                        )
                    )
    
