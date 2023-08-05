### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.adapter.title package

$Id: interfaces.py 49627 2008-01-21 15:31:34Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49627 $"
 
from zope.interface import Interface
from zope.schema import TextLine
                
                
class ITitle(Interface) :
    """ Interface ITitle
    
        title - title of object
    """

    title = TextLine(title=u"Title",
                     description=u"Title of object")
