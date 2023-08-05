### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.adapter.path package

$Id: interfaces.py 49951 2008-02-06 20:16:04Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49951 $"
 
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
