### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Object size interface

$Id: interfaces.py 51874 2008-10-20 17:22:49Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"

from zope.interface import Interface
from zope.schema import Int, Field

class IRecordSize(Interface):
    """Record Size interface"""

    size = Int(
        title=u"Size",
        description=u"Size of database record",
        default=0,
        required=True)


