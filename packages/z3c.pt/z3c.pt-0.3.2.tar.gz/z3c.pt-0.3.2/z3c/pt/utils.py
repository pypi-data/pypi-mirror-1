import zope.i18n

import cgi
from StringIO import StringIO

def handler(key=None):
    def decorate(f):
        def g(node):
            if key is None:
                return f(node, None)
            return f(node, node.get(key))
        g.__ns__ = key
        return g
    return decorate

def initialize_i18n():
    return (None, zope.i18n.translate)

def initialize_tal():
    return ({}, repeatdict())

def initialize_helpers():
    return (cgi.escape, object())

def initialize_stream():
    return StringIO()
    
def getLanguage(request):
    return ''

s_counter = 0

class scope(list):
    def __init__(self, *args):
        global s_counter
        self.hash = s_counter
        s_counter += 1

    def __hash__(self):
        return self.hash

class repeatitem(object):
    def __init__(self, iterator, length):
        self.length = length
        self.iterator = iterator
        
    @property
    def index(self):
        return self.length - len(self.iterator) - 1
        
    @property
    def start(self):
        return self.index == 0

    @property
    def end(self):
        return self.index == self.length - 1

    def number(self):
        return self.index + 1

    def odd(self):
        return bool(self.index % 2)

    def even(self):
        return not self.odd()

class repeatdict(dict):
    def __setitem__(self, key, iterator):
        try:
            length = len(iterator)
        except TypeError:
            length = None
            
        dict.__setitem__(self, key, (iterator, length))
        
    def __getitem__(self, key):
        value, length = dict.__getitem__(self, key)

        if not isinstance(value, repeatitem):
            value = repeatitem(value, length)
            self.__setitem__(key, value)

        return value
