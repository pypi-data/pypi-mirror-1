### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.adapter.title package

$Id: interfaces.py 50588 2008-02-07 06:38:04Z corbeau $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50588 $"
 
from zope.interface import Interface
from zope.schema import TextLine
                
                
class ITitle(Interface) :
    """ Interface ITitle
    
        title - title of object
    """

    title = TextLine(title=u"Title",
                     description=u"Title of object")
