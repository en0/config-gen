from os import environ
from os.path import join
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from exception import KeystoreExistsException
from keystore import Keystore


class Library(object):
    def __init__(self, path=None, fp=None):
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
        _store = name.upper()

        if _store in self._store_cache:
            return self._store_cache[_store]

        try:
            _ks_type = self._cp.get(_store, "type")
            _uri = self._cp.get(_store, "uri")

        except (NoOptionError, NoSectionError):
            raise Exception(
                "This store does not exist or is not properly formated"
            )

        ks = Keystore(_ks_type)
        ks.load(_uri)

        self._store_cache[_store] = ks

        return ks

    def add_keystore(self, name, ks):
        _store = name.upper()

        if self._cp.has_section(_store):
            raise KeystoreExistsException("That keystore is already added")

        if _store != "DEFAULT":
            self._cp.add_section(_store)

        self._cp.set(_store, "type", ks.ks_type)
        self._cp.set(_store, "uri", ks.uri)

        self._store_cache[_store] = ks

    def save(self):
        if self._fp:
            self._cp.write(self._fp)
        else:
            with open(self._path, 'w') as fp:
                self._cp.write(fp)

    @property
    def stores(self):
        _ret = self._cp.sections()
        if self._cp.has_option("DEFAULT", "type"):
            _ret.insert(0, "DEFAULT")
        return [x.lower() for x in _ret]
