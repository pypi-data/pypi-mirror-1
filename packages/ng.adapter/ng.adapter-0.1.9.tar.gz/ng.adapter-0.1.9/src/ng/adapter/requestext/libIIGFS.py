__doc__ = """\
Проект: IIGFS
Начато: Sun Sep 24 03:12:37 MSK 2000
Автор:  Andrey Orlov  (c) 2002
Верcия: $Id: libIIGFS.py 51772 2008-09-23 19:47:45Z cray $

Название:
        IIGFS / Библиотека вспомогательных функций
        
Описание:        
        Данная библиотека содержит общеупотребительные
        функции, используемые различными модулями. 
        За редким исключением, все функции включены в
        класс libIIGFS_mixin, который 
        использован как суперкласс во всех объектах IIGFS.

        Некотороые функции имееют лишь историческое
        значение и использовать их не рекомендуется.

Лицензия:
        GPL
        
Гарантия и отвественность :
        Никаких гарантий и ответственности

"""
__version__ = '$Revision: 51772 $'[10:-1]
# $Source: /var/lib/cvs/IIGFS/zope/Products/MOFS/libIIGFS.py,v $

debug = 0

import urllib
import string
import cgi
import re
from marshal import loads,dumps
from zlib import decompress,compress
from base64 import encodestring,decodestring
from Globals import MessageDialog
import DateTime 
trivial_trancetable = string.maketrans('','')
from AccessControl.SecurityManagement import getSecurityManager

from marshal import loads
from zlib import decompress
from urllib import unquote

#compress = lambda x : x
#decompress = lambda x : x

CantUnpack = 'Can not unpack data'

Unauthorized = 'Unauthorized'

class libIIGFS_mixin :
    """Библиотека полезных методов, отдаваемых в пространство имен Z-сервера
    В последствии нужно будет воткнуть библиотечку в dtml.

    """

    def request_setstart(self,seq,start_id='start_id',start='start',check=None) :
        """ Установить в запрсе поле start равным индексу элемента с
        идентификатором start_id в списке объектов, аргументы:

        seq - список объектов, который будет скролирован;

        start_id - имя переменной запроса, содержащей стартовый
        иденификатор;

        start - имя переменной запроса, в которую будет внесен стартовый
        индекс;

        Функция возвращает список объектов неизменым. """

        if self.REQUEST.has_key(start_id) :
            start_id = self.REQUEST[start_id] 
            for n in range(0,len(seq)) :
                if seq[n].getId() == start_id :
                        self.REQUEST[start] = n+1
                        break
        else :
            if check :
                raise 'NotFound', "Объект %s не существует" % start_id
        return seq

    def request_filter_keys(self,REQUEST,exclude=(),include=None,use_include=None) :
        """ Вернуть отфильтрованный список ключей запроса
        
        REQUEST - запроc,
        include - если не равно None и флаг use_include не равен 0, то в
                список войдут только перечисленные в этом атрибуте ключи,
        exclude - перечисленные ключи не войдут в список,
        use_include - если равен 0, то параметр include не будет
                использован.  
        """


        if include is None or (use_include==0) :
            include = REQUEST.form.keys()
        else :
            if type(include) is type('') :
                include = (include,)
            include = map(lambda x : x.split(':')[0], include)
            include = filter(REQUEST.form.has_key,include)

        if type(exclude) is type('') :
            exclude = (exclude,)

        exclude = map(lambda x : x.split(':')[0], exclude)
        return filter( lambda x,e=exclude : not (x in e), include)


    def request_filter_hash(self,REQUEST,exclude=[],include=None,use_include=None) :
        """ Вернуть элементы запроса, отфильтрованные request_filter_keys и
        преобразованные в хэш имя -> значения. Элементы типа record отдаются
        поэлементно как ключи вида <элемент>.<атрибут>.  Парамтры см. 
        request_filter_keys.  """

        d = {}
        for attr in self.request_filter_keys(REQUEST,exclude,include,use_include) :
                value = REQUEST.form[attr]
                if isinstance(value,ZPublisher.HTTPRequest.record) :
                        for a1,v1 in value.items() :
                                d['%s.%s:record' % (attr,a1)] = v1
                else :
                        d[attr] = value
        return d

    def request_filter_hidden(self,REQUEST,exclude=[],include=None,use_include=None) :
        """ Вернуть элементы запроса, отфильтрованные request_filter_keys и
        преобразованные в элементы ввода HIDDEN, парамтры см.
        request_filter_keys 
        """

        s = ''
        for a,v in self.request_filter_hash(REQUEST,exclude,include,use_include).items() :
            t = type(v)
            if  t is type(0) :
                s = s + '<input type=hidden name="%s:int" value="%i">' % (a,v)
            elif t is type([]) or t is type(()) :
                for vs in v :
                    s = s + '<input type=hidden name="%s:list" value="%s">' % (a,cgi.escape(str(vs),1))
            else :
                s = s + '<input type=hidden name="%s" value="%s">' % (a,cgi.escape(str(v),1))
        return s

    def request_filter_query(self,REQUEST,exclude=[],include=None,use_include=None) :
        """ Вернуть строку query, построенную из элементов запроса,
        возвращенных request_filter_keys
        """

        s = ''
        for a,v in self.request_filter_hash(REQUEST,exclude,include,use_include).items() :
            t = type(v)
            if  t is type(0) :
                s = s + '%s:int=%i&' % (a,v)
            elif t is type([]) or t is type(()) :
                for vs in v :
                    s = s + '%s:list=%s&' % (a,urllib.quote_plus(str(vs)))
            else :
                s = s + '%s=%s&' % (a,urllib.quote_plus(str(v)))

        return s

    def request_pack_hash(self,**kw) :
        """ Вернуть упакованный методом request_pack хэш аргументов """
        return self.request_pack(kw)

    def request_unpack_hash(self, query) :
        """ Вернуть результат распаковки query методом request_unpack. Если
        типа результата - хэш, то его ключи копируются в хеш form.
        """
        hash = self.request_unpack(query)
        if type(hash) == type({}) :
            for attr,value in hash.items() :
                self.REQUEST.form[attr] = value
                self.REQUEST[attr] = self.REQUEST.form[attr]
        return hash

    def request_pack(self,item) : 
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

#       print "(len(z),len(s)) = ",len(z),len(s)
        return string.translate(encodestring(v),string.maketrans('/+','-:') ,'\012====')

    def request_unpack(self,query) :
        """ Вернуть распакованое значение параметра query, ранее
        запакованное методом request_pack
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

    def request_ishere(self,url=None,right_margin=None,left_margin=None) :
        """ Проверить факт того, что объект соотвествующий данному url
        является контейнером запрашиваемого объекта, аргументы:

        url - путь к объекту, полученный absolute_url(1), если не указан -
                используется путь к текущему объекту,
        right_margin - количество незначащих элементов в конце url, если не
                указан - то все значащие,
        left_margin -  количество незначащих элементов в начале url, если не
                указан - то все значащие,

        Возвращает 1 при успешной проверке.
        """

        if url is None :
            url = self.absolute_url(1)

        ur = string.split(url,'/')
        if right_margin : ur = ur[0:-right_margin]
        if left_margin  : ur = ur[0: left_margin]

        vr = list(self.REQUEST.get('VirtualRootPhysicalPath',[''])[1:])
        qr = string.split(self.REQUEST.PATH_INFO,'/')[1:]
        if debug :
            print '------------------- request_ishere'
            print 'VR:',vr
            print 'UR,QR 1:',ur,qr

        if vr == ur[0:len(vr)] :
            ur = ur[len(vr):]

        if vr == qr[0:len(vr)] :
            qr = qr[len(vr):]

        if debug : print 'UR,QR 2:',ur,qr

        if qr[0:len(ur)] == ur :
            return 1

        return None

    def request_check(self,**kw) :
        """ Проверить переменные запроса на соответствие указанным
        регулярным выражениям.  Имена передаваемых аргументов совпадают с
        именами проверяемых переменных запроса.
        """

        for val,checks in kw.items() :
            if (len(checks) == 2) and (type(checks[0]) != type(())) and (type(checks[0]) != type([])) :
                checks = (checks,)
            for r,msg in checks :
                reg = re.compile(r[1:])
                if r[0]=='-' :
                    if reg.search(self.REQUEST[val]) : self.request_msg_append(val,msg)
                elif r[0]=='+' :
                    if not reg.search(self.REQUEST[val]) : self.request_msg_append(val,msg)
                else :
                    raise ValueError,"Invalid symbol %s in regexp of (%s,%s,%s): first symbol must be '-' or '+'" % (r[0],val,r,msg)
        return self.request_msg_check()


    def zsql_method_scroll(self,method,key='start',size=10,exclude=[],include=None,REQUEST=None,**kw) :
        """ Вернуть результаты вызова ZSQL метода, обработанные методом zsql_result_list. 
        
        При вызове ZSQL метода ему передаются параметры настройки прокрутки (start & size). Аргументы см.
        в zsql_result_scroll."""

        if REQUEST is not None :
            for arg,val in REQUEST.form.items() :
                kw[arg] = val

        kw['start'] = max(0,int(self.request_default(key,1)) - 1)
        kw['size']  = int(size)+1
        return self.zsql_result_scroll(
            apply(method,(),kw),
            key,size,exclude,include)

    def zsql_result_scroll(self,l=None,key='start',size=10,exclude=[],include=None,r=None) :
        """ Добавляет в список результатов l запроса mysql поля,
        ответственные за прокрутку списка:

        previous-sequence-start-number -- стартовый номер предыдущего блока
            последовательности или None;

        next-sequence-start-number -- стартовый номер следующего блока
            последовательности или None;

        previous-sequence-query -- запрос за предыдущей последовательностью;

        previous-sequence-query -- запрос за следующей последовательностью;

        Длина блока списка - size, переменная запроса используемая для
        прокрутки - key, параметры exclude & include аналогичны описанию
        методов request_filter* и используются при составлении ссылок
        дальше-раньше.

        Метод возвращает список хэшей.  
        """

        if not self.REQUEST.has_key(key) :
            start = 0
        else :
            start = max(int(self.REQUEST[key])-1,0)

        if (r is None) and (l is not None) :
            try :
                r = l.dictionaries()
            except AttributeError :
                r = l
        d = {}
        d['previous-sequence-start-number']       = None
        d['next-sequence-start-number']           = None
        d['previous-sequence-query']              = None
        d['next-sequence-query']                  = None
        d['previous-sequence-url']                = None
        d['next-sequence-url']                    = None

        qs = self.request_filter_query(self.REQUEST,exclude=[key]+list(exclude),include=list(include))
        if start > 0 :
            d['previous-sequence-start-number'] = max(start+1-size,1)
            d['previous-sequence-query'] = '%s%s=%u' % (qs,key,d['previous-sequence-start-number'])
            d['previous-sequence-url'] = self.REQUEST['URL1']+'?'+d['previous-sequence-query']
            
        if len(r) > 0 :
            if len(r) > size :
                d['next-sequence-start-number'] = start + 1 + size
                d['next-sequence-query'] = '%s%s=%u' % (qs,key,d['next-sequence-start-number'])
                d['next-sequence-url'] = self.REQUEST['URL1']+'?'+d['next-sequence-query']
                r = r[0:size]

            for a,v in d.items() :
                r[0][a] = v
                r[-1][a] = v

        return r

    marked_list = zsql_result_scroll
    marked_list_db = zsql_method_scroll

    def cookielist_unpack(self,prefix='fld') :
        # Вернуть распакованный список, сохраненный в куке с префиксом имени
        # fld. Для редактирования списка используется функция
        # cookielist_edit

        if self.REQUEST.has_key(prefix + '_list') :
            try :
                return self.request_unpack(self.REQUEST[prefix + '_list'])
            except CantUnpack :
                pass
        return []
        

    def cookielist_edit(self,prefix='fld',add=[],lifeperiod=None, path='/') :
        """ Редактировать список хешей, хранимых в куке c префиксов fld,
        аргументы:

        prefix - префикс переменных запроса, обслуживающих данный редактор,

        add - список добавляемых хешей,

        lifeperiod - время жизни кука, если не указано - то используется
        сессионный кук,

        path - путь при хранении кука (см. RFC),

        Возможные команды запроса:

        <PREFIX>_add - добавить элементы концу списка, список элементов
                должен быть передан в аргументе add,

        <PREFIX>_delete - удалить элементы из списка, список номеров
                удаляемых элементов передается в <PREFIX>_id, элементы
                нумеруются с нуля.

        <PREFIX>_first - переместить элементы в начало списка, список
                номеров удаляемых элементов передается в <PREFIX>_id,
                элементы нумеруются с нуля.

        <PREFIX>_clean - Очистить корзину полностью

        Метод заносит в сообщения запроса с ключом <PREFIX>_list сообщения о
        выполненных операциях.
        """

        l = self.cookielist_unpack(prefix)
        if self.REQUEST.has_key(prefix + '_add') :
            if type(add) is not type([]) :
                l.extend([add])
            else :
                l.extend(add)

        elif self.REQUEST.has_key(prefix + '_delete') :
            try :
                di = map(lambda x: int(x), self.REQUEST[prefix + '_id'])
            except KeyError :
                self.request_msg_append(prefix + '_list', 'Не выбрано ни одного элемента для удаления')
                return l

            di.reverse()
            try :
                for item in di :
                    del(l[item])
            except IndexError:
                self.request_msg_append(prefix + '_list', 'Попытка удаления несуществующего элемента')
                return self.cookielist_unpack(prefix)
    
        elif self.REQUEST.has_key(prefix + '_first') :
            try :
                di = map(lambda x: int(x), self.REQUEST[prefix + '_id'])
            except KeyError :
                self.request_msg_append(prefix + '_list', 'Не выбрано ни одного элемента для помещения в начало')
                return l
            
            try :
                n = 0
                for item in di :
                    l.insert(n,l[item])
                    n = n + 1
                    del(l[item+1])
            except IndexError :
                self.request_msg_append(prefix + '_list', 'Попытка помещения в начало ранее удаленных элементов')
                return self.cookielist_unpack(prefix)
	elif self.REQUEST.has_key(prefix + '_clear') :
	    l = []
        else :
            return l
            
        self.cookielist_set(l,prefix,lifeperiod,path)
        return l

    def cookielist_set(self,l,prefix='fld',lifeperiod=None,path='/') :
        """ Упаковать и установить кук со списком """
        cookie = self.request_pack(l)
        if debug : print 'Размер корзины',len(cookie) 
        if len(cookie) > 1024 :
                self.request_msg_append(prefix + '_list', 'Операция не была выполнена, т.к. корзина переполнена')
                return self.request_unpack(self.REQUEST[prefix + '_list'])

        d = {}
        if lifeperiod :
                d['expires'] = (DateTime.DateTime()+lifeperiod).rfc822()
        if path :
		if path[0] != '/' :
		   path = '/' + path
                d['path'] = path

	#print 'path',path
        apply(self.REQUEST.RESPONSE.setCookie,(prefix + '_list',cookie),d)

        return l


    _type_url_prefix = re.compile('^((http)|(ftp)|(mailto)|(int)|(javascript))[:/]*')
    _type_url_full = re.compile('^(((http)|(ftp)|(mailto))*.*\.)|(int|javascript).*$')

    def type_url_tunning(self,url='') :
        #""" Вернуть нормализованный URL. URL должен включать протоколы
        #http, ftp, mailto, int, javascript.  Если протокол отсутствует - по
        #умолчанию подставляется http:// """

        url = string.strip(url)
        if self._type_url_full.match(url) :
                if self._type_url_prefix.match(url) :
                        return url
                else :
                        return 'http://' + url

        return ''

    _type_email_check = re.compile('([A-Za-z_.0-9]+@([0-9A-Za-z_]+\.)+[0-9A-Za-z_]*)').search

    def type_email_tunning(self,email='') :
        # вернуть нормализованный email
        em = self.type_email_check(email)
        if em : 
                return em.group(0)
        return ''

    def type_email_check(self,email='') :
        return self._type_email_check(email)

