from os import environ
from os.path import join
from ConfigParser import SafeConfigParser
from exception import KeystoreExistsException, InvalidKeystoreException
from exception import UnkonwnAdapterException
from keystore import Keystore
from .adapaters import get_adapters


def _normalize_store_name(s):
    return "_DEFAULT" if s.upper() == "DEFAULT" else s.upper()


class Library(object):
    def __init__(self, path=None, fp=None, adapters=None):
        self._adapters = adapters or get_adapters()
        self._cp = SafeConfigParser()
        self._store_cache = {}
        if fp:
            self._path = None
            self._fp = fp
            self._cp.readfp(fp)
        else:
            self._fp = None
            self._path = path or join(environ["HOME"], ".conflib.ini")
            self._cp.read(self._path)

    def get_keystore(self, name):
        _store = _normalize_store_name(name)

        if _store in self._store_cache:
            return self._store_cache[_store]

        if not self._cp.has_section(_store):
            raise InvalidKeystoreException("Store does not exist")

        _opts = dict(self._cp.items(_store))

        if "type" not in _opts or "uri" not in _opts:
            raise InvalidKeystoreException(
                "This store is not properly formated"
            )

        if _opts["type"] not in self._adapters:
            raise UnkonwnAdapterException(
                "Unkonwn keystore type '{}'".format(_opts["type"])
            )

        _uri = _opts["uri"]
        _type = _opts["type"]

        del _opts["type"]
        del _opts["uri"]

        ks = Keystore(self._adapters[_type])
        ks.load(_uri, **_opts)

        self._store_cache[_store] = ks

        return ks

    def add_keystore(self, name, ks_type, uri, **kwargs):
        _store = _normalize_store_name(name)

        if self._cp.has_section(_store):
            raise KeystoreExistsException("That keystore is already added")

        kwargs["type"] = ks_type
        kwargs["uri"] = uri

        self._cp.add_section(_store)
        for k, v in kwargs.iteritems():
            self._cp.set(_store, k, v)

    def remove_keystore(self, name):
        _store = _normalize_store_name(name)

        if not self._cp.has_section(_store):
            raise InvalidKeystoreException("Store does not exist")

        self._cp.remove_section(_store)

    def save(self):
        if self._fp:
            self._cp.write(self._fp)
        else:
            with open(self._path, 'w') as fp:
                self._cp.write(fp)

    @property
    def stores(self):
        _ret = []
        for x in self._cp.sections():
            if x != "_DEFAULT":
                _ret.append(x.lower())
            else:
                _ret.append("default")
        return _ret

