
### -*- coding: utf-8 -*- #############################################
#######################################################################
""" IRequest Adapter to IRequestExt interface

$Id: requestext.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.publisher.browser import Record

import urllib
import string
import cgi
import re
from marshal import loads,dumps
from zlib import decompress,compress
from base64 import encodestring,decodestring
from datetime import datetime
import time

from interfaces import IRequestExt

class CantUnpack(Exception):
    """Can't unpack data"""


class RequestExt(object) :
    implements(IRequestExt)

    exclude=()
    include=None
    use_include=False

    def __init__(self, request):
        super(RequestExt, self).__init__(request)
        self.request = request

    def setParameters(self, exclude=(), include=None, use_include=False) :
        """
            Set filter parameters:
            include -- if not equal None and use_include flag is True, then list
                will be content only keys from include;
            exclude -- this keys will be excluded from list anyway;
            use_include -- if equal False, then parameter include can't be used. 
        """
        
        if type(exclude) is type('') :
            self.exclude = (exclude,)
        else :
            self.exclude = exclude
            
        if type(include) is type('') :
            self.include = (include,)
        else :            
            self.include = include
        self.use_include = use_include

    def keys(self) :
        """ Return list of request keys after filering """

        if self.include is None or (self.use_include == 0) :
            include = self.request.form.keys()
        else :
            include = [y for y in 
                        [ x.split(':')[0] for x in self.include ] 
                        if self.request.form.has_key(y) ]

        exclude = [ x.split(':')[0] for x in self.exclude]
        return [ x for x in include if not x in exclude ]

    def _parseRecordElement(self, attr, value):
        d = {}
        t = type(value)

        if isinstance(value, Record) :
            for a1,v1 in value.items() :
                d['%s.%s:record' % (attr, a1)] = v1
        else:
            d[attr] = value

        return d

    def _parseSequenceElement(self, attr, value, postfix=''):

        l = []
        t = type(value)
        newPostfix = ''
        if t == type([]):
            newPostfix = ':list' + postfix
        elif t == type(()):
            newPostfix = ':tuple' + postfix

        if newPostfix:
            for v1 in value:
                l.append(self._parseElement(attr, v1, newPostfix))

        return l

    def _parseElement(self, attr, value, postfix=''):
        t = type(value)
        newPostfix = ''
        if t == type(0):
            newPostfix = ':int'
        elif t == type(0.8):
            newPostfix = ':float'
        elif t == type(99999999999999):
            newPostfix = ':long'
        elif t == type(''):
            newPostfix = ':string'

        return (attr + newPostfix + postfix, value)

    def dict(self) :
        """ Return request items as dict key->value """
        
        d = {}
        for attr in self.keys() :
                value = self.request.form[attr]
                d.update(self._parseRecordElement(attr, value))

        return d

    def list(self):
        """ Return request items as dictionary list """
        l = []
        for a,v in self.dict().items() :
            l.extend(self._parseSequenceElement(a, v) or [self._parseElement(a, v)])

        return l

    def hidden(self,**kw) :
        """ Return request items as hidden HTML input tags"""

        s = ''
        for a,v in self.list() +kw.items():
            s = s + '<input type=hidden name="%s" value="%s">' % (a,cgi.escape(str(v),1))
        return s

    def query(self,**kw) :
        """ Return query string """
        s = ''
        for a,v in self.list() +kw.items():
            s = s + '%s=%s&' % (a,urllib.quote_plus(str(v)))

        return s

    def pack_dict(self,**kw) :
        """ Вернуть упакованный методом pack хэш аргументов """
        return self.pack(kw)

    def unpack_dict(self, query) :
        """ Вернуть результат распаковки query методом unpack. Если
        тип результата - словарь, то его ключи копируются в словарь form.
        """
        hash = self.unpack(query)
        if type(hash) == type({}) :
            for attr,value in hash.items() :
                self.request.form[attr] = value
        return hash

    def pack(self, item) :
        """ Вернуть параметр item, упакованный для передачи через запрос.
        Обычный метод упаковки - marshal + zip + base64 + "нормализация"
        base64.
        """

        s = dumps(item)
        z = compress(s)

        if len(z) >= len(s) :
            v = 's' + s
        else :
            v = 'z' + z

        return string.translate(encodestring(v),string.maketrans('/+','-:') ,'\012====')

    def unpack(self,query) :
        """ Вернуть распакованое значение параметра query, ранее
        запакованное методом pack
        """
        l=len(query)
        try :
            v = decodestring(
                        string.translate(
                            query,string.maketrans('-:','/+')
                        )
                        + ('=' * ((l+3)/4*4-l))
                )
            if v[0] == 'z' :
                return loads(decompress(v[1:]))
            else :
                return loads(v[1:])
        except :
            raise CantUnpack

class RequestExtView(RequestExt) :
    implements(IRequestExt)

    def __init__(self, context, request):
        self.context = context
        self.request = request

#
#        self.request.response.setHeader('Pragma', 'no-cache')
#        self.request.response.setHeader('Cache-Control', 'no-cache')
#        self.request.response.setHeader('Expires',
#            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()))
#            )
#        self.request.response.setHeader('Last-Modified',
#            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()))
#            )
#