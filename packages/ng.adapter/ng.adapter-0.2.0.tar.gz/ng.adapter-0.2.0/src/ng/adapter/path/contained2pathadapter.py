### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Contained2PathAdapter class for the Zope 3 based ng.adapter.path package

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"


from zope.interface import implements
from zope.app.container.interfaces import IContained
from interfaces import IPath
from zope.component import adapts
from ng.adapter.title.interfaces import ITitle
from pathadapterbase import PathAdapterBase


class Contained2PathAdapter(PathAdapterBase) :

    implements(IPath)
    adapts(IContained)
   
    @property
    def titledpath(self) :
        return "/".join([
            IPath(IContained(self.context).__parent__).titledpath,
            ITitle(self.context).title])
    
    @property
    def path(self) :
        return "/".join([IPath(IContained(self.context).__parent__).path, self.name])

    @property    
    def name(self) :
        return IContained(self.context).__name__
        
    def _tailpath(self,path) :
        next = IPath(IContained(self.context).__parent__)
        return next._tailpath(
            path + ("/".join((next.name,path[-1])),)
        )
