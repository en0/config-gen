class Keystore(object):
    def __init__(self, adapater_class):
        self.AdapaterClass = adapater_class
        self._uri = None

    def __getitem__(self, key):
        return self._adapater.get_value(key)

    def __setitem__(self, key, value):
        self._adapater.set_value(key, value)

    def __delitem__(self, key):
        self._adapater.remove_key(key)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return iter(self.keys())

    @property
    def __dict__(self):
        _ret = {}
        for k in self.keys():
            _ret[k] = self.__getitem__(k)
        return _ret

    def keys(self):
        return self._adapater.get_keys()

    def values(self):
        return [self.__getitem__(k) for k in self]

    def items(self):
        return [(k, self[k]) for k in self]

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        def _i():
            for k in self:
                yield self[k]
        return _i()

    def iteritems(self):
        def _i():
            for k in self:
                yield (k, self[k])
        return _i()

    def load(self, uri, **kwargs):
        self._uri = uri
        self._adapater = self.AdapaterClass(uri, **kwargs)

    @property
    def ks_type(self):
        return self.AdapaterClass.name

    @property
    def uri(self):
        return self._uri
