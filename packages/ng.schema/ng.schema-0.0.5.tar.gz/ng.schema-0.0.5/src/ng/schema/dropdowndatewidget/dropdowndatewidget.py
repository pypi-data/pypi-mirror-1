### -*- coding: utf-8 -*- #############################################
#######################################################################
"""DropDownDateWidget class for the Zope 3 based ng.schema.dropdownwidget package

$Id: dropdowndatewidget.py 51938 2008-10-23 08:22:07Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51938 $"

from zope.app.form.browser.textwidgets import TextWidget
import datetime
import time


class DropDownDateWidget(TextWidget) :

    def __call__(self) :

        months_dict = {
            1:u'January', 2:u'February', 3:u'March',
            4:u'April', 5:u'May', 6:u'June',
            7:u'July', 8:u'August', 9:u'September',
            10:u'October', 11:u'November', 12:u'December'
        }
        
        years = u''
        months = u''
        days = u''
        
        for i in range(1900, 2101):
            years = years + u'<option value="%d">%d</option>' % (i, i)

        for i in range(1, 13):
            months = months + u'<option value="%d">%s</option>' % (i, months_dict[i])

        for i in range(1, 32):
            days = days + u'<option value="%d">%d</option>' % (i, i)
            
        code = u"""<select name="year" size="1">
                     %s
                   </select>
                   <select name="month" size="1">
                     %s
                   </select>
                   <select name="day" size="1">
                     %s
                   </select>
                """ % (years, months, days)

        date = str(self._getFormValue()).split(u'-')
        
        try :
            code = code.replace('<option value="%d">%d</option>' % (int(date[0]), int(date[0])),
                                '<option value="%d" selected>%d</option>' % (int(date[0]), int(date[0]))
                               )

            code = code.replace('<option value="%d">%s</option>' % (int(date[1]), months_dict[int(date[1])]),
                                '<option value="%d" selected>%s</option>' % (int(date[1]), months_dict[int(date[1])])
                               )

            code = code.replace('<option value="%d">%d</option>' % (int(date[2]), int(date[2])),
                                '<option value="%d" selected>%d</option>' % (int(date[2]), int(date[2]))
                               )
        except ValueError:
            pass
        return code
    
    def hasInput(self) :
        return u'year' in self.request.form

    def getInputValue(self) :
        year = int(self.request.form[u'year'])
        month = int(self.request.form[u'month'])
        day = int(self.request.form[u'day'])
        
        value = datetime.date(year, month, day)

        return value
