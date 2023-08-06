### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.hello.world package

$Id: interfaces.py 52462 2009-02-05 12:08:58Z corbeau $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52462 $"

from zope.interface import Interface

from zope.schema import TextLine, Set, Choice

from zope.schema.vocabulary import SimpleVocabulary
#    vocabulary = SimpleVocabulary.fromValues([u"раз",u"два"])

class IDemoMultiselectWidget(Interface) :

    someset = Set(
        title = u'Some Set',
        description = u'Some Set',
        value_type = Choice(vocabulary = SimpleVocabulary.fromValues([u"one",u"two", u"three"])),
        required = False)

    onemoreset = Set(
        title = u'One More Set',
        description = u'One More Set',
        value_type = Choice(vocabulary = SimpleVocabulary.fromItems(((u"four",4), (u"five",5), (u"six",6)))),
        required = False)
        