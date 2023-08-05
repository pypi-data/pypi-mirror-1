### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.mtime package

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.interface import Interface
from zope.schema import Float,TextLine

class IMTime(Interface):

    mtime = Float(
        title=u"Modification time",
        description=u"Last modification time in second from Unix Epoch"
        )

    def strftime(format=TextLine(title=u"TimeDate Format")) :
        """ Return datetime as string using format argument """
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(0))
