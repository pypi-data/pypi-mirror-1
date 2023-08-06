### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: ianytitleadapter.py 49001 2007-12-24 13:29:26Z antel $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49001 $"

import sys
import re
from interfaces import IAnyTitle
from zope.interface import implements
from zope.component import adapts
from zope.app.container.interfaces import IContained
from zope.component import subscribers

class AnyTitleAdapter(object) :
    implements(IAnyTitle)
    adapts(IContained)

    shorttitlelength = 18
    
    subword = " ... "
    
    lensubword = len(subword)    

    def __init__(self, ob) :
        self.context = ob
        
    @property
    def title(self) :
        for adapter in sorted (subscribers([self.context], IAnyTitle), reverse=True) :
            try :
                title = adapter.title
            except Exception, msg :
                print "title lookup in", adapter, "for",self.context, "fault:",msg
            else :                
                if title is not None :
                    title = title.strip()
                    if title :
                        return adapter.title
        return IContained(self.context).__name__
    
    @property
    def shorttitle(self) :

        titles = ( y for y in ( x.title.strip() for x in subscribers([self.context], IAnyTitle)) if y )
        
        try :
            title = titles.next()
        except StopIteration :
            title = IContained(self.context).__name__
        else :            
            for mtitle in titles :
                if (    (len(title) < len(mtitle) and len(mtitle) < self.shorttitlelength) 
                     or (len(title) > len(mtitle) and len(mtitle) > self.shorttitlelength) 
                     or (len(mtitle) < self.shorttitlelength < len(title))     ):
                    title = mtitle

        if len(title) < self.shorttitlelength : 
            return title

        title,flag = re.subn("\s[^\s]{%s,%s}\s" % ( 
                        len(title)-self.shorttitlelength+self.lensubword, 
                        len(title)-self.shorttitlelength+self.lensubword+3 )," ... ",title,1)

        if flag : 
            return title
        else :
            return ( title[:(self.shorttitlelength-self.lensubword)/2] 
                + self.subword
                + title[(len (title) - (self.shorttitlelength-self.lensubword)/2):] )

