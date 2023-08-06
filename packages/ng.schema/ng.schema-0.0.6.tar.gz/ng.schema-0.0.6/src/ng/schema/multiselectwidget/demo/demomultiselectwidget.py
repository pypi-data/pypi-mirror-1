### -*- coding: utf-8 -*- #############################################
#######################################################################
"""HelloWorld class for the Zope 3 based ng.hello.world package

$Id: demomultiselectwidget.py 52462 2009-02-05 12:08:58Z corbeau $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52462 $"

from persistent import Persistent
from zope.app.container.contained import Contained

class DemoMultiselectWidget(Contained, Persistent) :

    pass
