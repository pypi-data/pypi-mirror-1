### -*- coding: utf-8 -*- #############################################
#######################################################################
"""NameChooser adapter

$Id: namechooser.py 14068 2007-12-02 18:13:16Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 14068 $"

from zope.interface import Interface
from ng.adapter.title.interfaces import ITitle
import re
match = re.compile("^(?P<name>.*[^0-9])(?P<number>[0-9]+)$").match
                
class NameChooser(object) :

    def __init__(self,context) :
        self.context = context

    def checkName(self, name, object) :
        """Check whether an object name is valid.
            Raises a user error if the name is not valid. """
        return True
     
    def chooseName(self, name, object) :
        """ Choose a unique valid name for the object
            The given name and object may be taken into account when choosing the name. """

        if name :
            title = name
        else :            
            try :
                title = ITitle(object).title
            except TypeError,msg :
                print "Can't get title becouse of",msg
                title = object.__class__.__name__

        while title in self.context :
            res = match(title)
            if res :
                d = res.groupdict()
                d['number']=int(d['number'])+1
                title = "%(name)s%(number)u" % d
            else :                
                title = title + "0"
                                    
        return title            
