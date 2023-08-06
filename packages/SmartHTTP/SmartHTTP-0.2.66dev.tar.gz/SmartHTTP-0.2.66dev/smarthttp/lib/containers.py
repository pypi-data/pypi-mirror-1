# -*- coding: utf-8 -*-
"""
Custom container implementations
"""
class SmartDict(dict):
    _internal = ['_internal', '_default', '_dict', '_join', '__getitem__', '__setitem__', '__getattribute__', '__setattr__', 'keys']
    _default = None
    _dict    = None
    def __init__(self, value=None, default=None):
        if type(value) == dict:
            self._dict = value
        else:
            self._dict = {}
        self._default = default

    def _join(self, d):
        _dict = self._dict
        for key in d:
            _dict[key] = d[key]
        return self

    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        _dict = self._dict
        if not item in _dict:
            _default = self._default
            if type(_default) == type:
                _dict[item] = _default()
            else:
                _dict[item] = _default
        return _dict[item]
    def __setitem__(self, item, value):
        self._dict.__setitem__(item, value)
        
    def __getattribute__(self, item):
        _internal = object.__getattribute__(self, '_internal')
        if item in _internal:
            return object.__getattribute__(self, item)
        else:
            return self[item]
    def __setattr__(self, item, value):
        _internal = object.__getattribute__(self, '_internal')
        if item in _internal:
            return object.__setattr__(self, item, value)
        else:
            return self.__setitem__(item, value)

def strdict(d):
    """
    Turn all keys into str
    >>> strdict({u'uni':0, 'str':0, 1:0}).keys() == ['uni', 'str', '1']
    True
    """
    nd = {}
    for k in d:
        v = d[k]
        nd[str(k)] = v
    return nd
