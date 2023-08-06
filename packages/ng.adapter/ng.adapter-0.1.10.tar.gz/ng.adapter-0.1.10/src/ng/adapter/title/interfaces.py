### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.adapter.title package

$Id: interfaces.py 51874 2008-10-20 17:22:49Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"
 
from zope.interface import Interface
from zope.schema import TextLine
                
                
class ITitle(Interface) :
    """ Interface ITitle
    
        title - title of object
    """

    title = TextLine(title=u"Title",
                     description=u"Title of object")
