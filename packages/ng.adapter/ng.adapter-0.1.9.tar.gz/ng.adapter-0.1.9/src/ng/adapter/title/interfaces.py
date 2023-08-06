### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.adapter.title package

$Id: interfaces.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"
 
from zope.interface import Interface
from zope.schema import TextLine
                
                
class ITitle(Interface) :
    """ Interface ITitle
    
        title - title of object
    """

    title = TextLine(title=u"Title",
                     description=u"Title of object")
