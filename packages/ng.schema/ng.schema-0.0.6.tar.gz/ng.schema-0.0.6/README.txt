The ng.schema product
=====================


The ng.schema is zope3 product developed to provide some interface (schema)
fields and widget. Current field and widget list are:

interfaceswitcher
-----------------
Field can be used to dynamic switch subinterfaces of
some interface;

Sample of use ::
        
    from ng.schema.interfaceswitcher.interfacechoicefield import InterfaceChoice
    from ng.schema.interfaceswitcher.interfacesetfield import InterfaceSet

    class IA(Interface) :
        pass
        
    class IA1(IA) :
        pass
        
    class IA2(IA) :
        pass
        
    class IOb(Interface) :
    
        ifc = InterfaceChoice(
            title=u'Interface of IA',
            interface = IA,
            )

        ifs = InterfaceSet(
            title=u'Interface of IA',
            interface = IA,
            with_title=True
            )

regexp
------
Product can be used to check input text line with some set of
regexp and customize text line with some rewrite rules before set.
    
Sample of use ::
        
    from ng.schema.regexp.regexpfield import Regexp        
    class IOb(Interface) :
        title = Regexp(title = u'Title',
            description = u'Title',
            default = u'',
            required = True,
            regexp = (
                  (False, u"^.*/.*$", u"Title do not content symbol '/'"),
                ),
            rewrite = (
                (u"^\s*(?P<name>\w+)\s*-\s*(?P<number>[0-9]+)\s*$", u"%(name)s-%(number)s"),
                (u"^\s*(?P<name>[^\s])\s*$", u"%(name)s"),
                )
            )

floatdayttime
-------------
The field allow present attribute containing float number as 
time string in "HH:MM:SS" format.

Sample of use::

    from ng.schema.floatdaytime.floatdaytime import FloatDayTime
    class IOb(Interface) :
        time = FloatDayTime(
            title = u"Time",
            description = u"Time of day",
            required = False,
            min=u'00:00',
            max=u'24:00',
            default=u'00:00'
            )

principalidwidget
-----------------
The widget allow automaticaly assign text field by user Id. The field display as not-editable field
with current user name as vaue. User name and id gets from request attributes.

Sample of use::

    <addform
        label="Add Article"
        name="AddArticle.html"
        schema="ng.content.article.interfaces.IDocShortLogo"
        content_factory="ng.content.article.article.article.Article"
        class=".nexturl.NextUrl"
        permission="zope.ManageContent"
	    layer="...interfaces.GreenpsySkin"
        set_before_add="title"
	    >
	    <widget 
		    field="author"
		    class="ng.schema.principalidwidget.principalidwidget.PrincipalIdWidget" />
    </addform>
    
dropdowndatewidget
------------------
The widget allow input date by means of select value from three dropdown list for
day, mounth and year.

Sample of use::

    <editform
        schema="..interfaces.IProfileAnnotation"
        for="..interfaces.IProfileAnnotation"
        label="Profile"
        name="profileannotation.html"
        permission="zope.ManageContent"
        menu="zmi_views" title="ProfileAnnotation" 
        >
        <widget field="birthday" class="ng.schema.dropdowndatewidget.dropdowndatewidget.DropDownDateWidget" />
   </editform> 
