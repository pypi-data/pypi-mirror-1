### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.adapter.path package

$Id: interfaces.py 50588 2008-02-07 06:38:04Z corbeau $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50588 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Tuple


class IPath(Interface) :
    """ Interface IPath.

        path - path from root object of Zope to current object
        
        titledpath - path from root object of Zope to current object,
            contains from titles ob objects
    """
    
    path = TextLine(title=u"Path",
                    description=u"Path from root object of Zope to current object")
    
    titledpath = TextLine(title=u"Titled path",
                          description=u"Titled path from root object of Zope to current object")

    tailpath = Tuple()
