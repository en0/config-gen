from ConfigParser import RawConfigParser
from urlparse import urlparse


class IniAdapter(object):

    name = "ini"

    def get_value(self, key):
        if not self._cp.has_option(self._section, key):
            return None
        return self._cp.get(self._section, key)

    def set_value(self, key, value):
        self._cp.set(self._section, key, value)
        self._is_dirty = True

    def remove_key(self, key):
        self._cp.remove_option(self._section, key)
        self._is_dirty = True

    def get_keys(self):
        return self._cp.options(self._section)

    def __init__(self, uri):
        _uri = urlparse(uri, scheme="file://")
        self._section = _uri.query.lower() or '_default'
        self._path = _uri.path

        if self._section == 'default':
            self._section = '_default'

        self._cp = RawConfigParser()
        self._cp.optionxform = str

        self._cp.read(self._path)
        self._is_dirty = False

        if not self._cp.has_section(self._section):
            self._cp.add_section(self._section)

    def __del__(self):
        if self._is_dirty:
            with open(self._path, 'w') as fp:
                self._cp.write(fp)
