### -*- coding: utf-8 -*- #############################################
#######################################################################
""" mtimeAdapter class that adapt IPersistent to IMTime

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.interface import implements
from zope.component import adapts
from persistent.interfaces import IPersistent
from interfaces import IMTime
import time

class mtimeAdapter(object):
    __doc__ = __doc__
    implements(IMTime)
    adapts(IPersistent)

    def __init__(self, context):
        self.context = context

    @property
    def mtime(self):
        if IPersistent(self.context)._p_changed:
            return time.time()
        else:
            return IPersistent(self.context)._p_mtime

    def strftime(self,format=u"%Y-%m-%d %H:%M:%S") :
        """ Return datetime as string using format argument """
        return time.strftime(format,time.localtime(self.mtime))
