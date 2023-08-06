# -*- coding: utf-8 -*-

"""General workarounds for different versions of Python."""


class property(object):
    
    "Emulate ``property()`` built-in with shiny new 2.6 features."
    
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self         
        if self.fget is None:
            raise AttributeError('unreadable attribute')
        return self.fget(obj)
    
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)
    
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)
    
    def getter(self, function):
        self.fget = function
        return self
    
    def setter(self, function):
        self.fset = function
        return self
    
    def deleter(self, function):
        self.fdel = function
        return self
