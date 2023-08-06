### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.куйгуые package

$Id: interfaces.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import Interface

class IRequestExt(Interface):

    def keys(exclude=(),include=None,use_include=None):
        """ Вернуть отфильтрованный список ключей запроса

        include - если не равно None и флаг use_include не равен 0, то в
                список войдут только перечисленные в этом атрибуте ключи,
        exclude - перечисленные ключи не войдут в список,
        use_include - если равен 0, то параметр include не будет
                использован.
        """

    def dict(exclude=[],include=None,use_include=None):
        """ Вернуть элементы запроса, отфильтрованные keys и
        преобразованные в словарь имя : значения. Элементы типа record отдаются
        поэлементно как ключи вида <элемент>.<атрибут>.  Парамтры см.
        keys.  """

    def list(exclude=[], include=None, use_include=None):
        """ Вернуть элементы запроса, отфильтрованные keys и
        преобразованные в список словарей. Параметры см. keys. """

    def hidden(exclude=[],include=None,use_include=None) :
        """ Вернуть элементы запроса, отфильтрованные keys и
        преобразованные в элементы ввода HIDDEN, парамтры см.
        keys
        """

    def query(exclude=[],include=None,use_include=None) :
        """ Вернуть строку query, построенную из элементов запроса,
        возвращенных keys
        """

    def pack_dict(**kw):
        """ Вернуть упакованный методом pack хэш аргументов """

    def pack_unpack_dict(**kw):
        """ Вернуть результат распаковки query методом unpack. Если
        типа результата - словарь, то его ключи копируются в словарь form.
        """

    def pack(item):
        """ Вернуть параметр item, упакованный для передачи через запрос.
        Обычный метод упаковки - marshal + zip + base64 + "нормализация"
        base64.
        """

    def unpack(query):
        """ Вернуть распакованое значение параметра query, ранее
        запакованное методом pack
        """
