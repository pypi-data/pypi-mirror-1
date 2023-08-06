### -*- coding: utf-8 -*- #############################################
#######################################################################
"""NameChooser adapter

$Id: namechooser.py 53381 2009-07-05 22:27:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 53381 $"

from zope.interface import Interface
from ng.adapter.title.interfaces import ITitle
import re
match = re.compile("^(?P<name>.*[^0-9])(?P<number>[0-9]+)$").match
unsafe = re.compile("[?]")

                
class NameChooser(object) :

    def __init__(self,context) :
        self.context = context

    def checkName(self, name, object) :
        """Check whether an object name is valid.
            Raises a user error if the name is not valid. """
        return True
     

    def getTitle(self, name, object) :
        if name :
            title = name
        else :            
            try :
                title = ITitle(object).title
            except TypeError,msg :
                print "Can't get title becouse of",msg
                title = object.__class__.__name__
        return title    

    def chooseName(self, name, object) :
        """ Choose a unique valid name for the object
            The given name and object may be taken into account when choosing the name. """

        title = self.getTitle(name,object)
    

        while title in self.context :
            res = match(title)
            if res :
                d = res.groupdict()
                d['number']=int(d['number'])+1
                title = "%(name)s%(number)u" % d
            else :                
                title = title + "0"
                                    
        return title            

class NameChooserSafe(NameChooser) :
    
    rewrite_rules = [
        (re.compile("[?]"),"."),
        (re.compile("[/]")," - "),
        (re.compile("\s+")," "),
        (re.compile("^\s+"),""),
        (re.compile("\s+$"),""),
    ]
    
    def rewrite(self, name) :
        print name
        for pattern, repl in self.rewrite_rules :
            name = re.sub(pattern, repl, name)
            print name
        return name
    
    def getTitle(self, name, ob) :
        return self.rewrite(super(NameChooserSafe,self).getTitle(name,ob))
        

class NameChooserSafeWithoutSpace(NameChooserSafe) :
    
    rewrite_rules = [
        (re.compile("[?]"),"."),
        (re.compile("[/]"),"-"),
        (re.compile("^\s+"),""),
        (re.compile("\s*(?P<sign>[.,;=\-+_?!:])\s*"),lambda x : x.groupdict()['sign']),
        (re.compile("\s+$"),""),
        (re.compile("\s+"),"_"),
    ]
    
            
            
           