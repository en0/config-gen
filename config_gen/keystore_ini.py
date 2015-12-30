from exception import ProfileNotFoundException, KeyNotFoundException
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from urlparse import urlparse
from os.path import split


class KeystoreIni(object):
    __VER__ = "ini.0.1"
    __KS_TYPE__ = "ini"

    def __init__(self, **kwargs):
        self._cp = RawConfigParser(defaults={"__ver__": self.__VER__})
        self._cp.optionxform = str

    @property
    def version(self):
        return self._cp.get("DEFAULT", "__ver__")

    @property
    def ks_type(self):
        return self.__KS_TYPE__

    @property
    def uri(self):
        return "file://{}".format("/".join(split(self._path)))

    @property
    def profiles(self):
        _ret = self._cp.sections()
        return ['default' if x == '_DEFAULT' else x.lower() for x in _ret]

    def get_keys(self, profile):
        _profile = profile.upper()
        _profile = "_DEFAULT" if _profile == "DEFAULT" else _profile
        try:
            _ret = self._cp.options(_profile)
        except NoSectionError:
            raise ProfileNotFoundException(
                "Profile '{}' does not exist.".format(profile)
            )
        return [x for x in _ret if x != '__ver__']

    def load(self, uri):
        _path = urlparse(uri, scheme="file://").path
        self._cp.read(_path)
        if not self._cp.has_option('DEFAULT', '__ver__'):
            self._cp.set("DEFAULT", "__ver__", self.__VER__)
        if not self._cp.has_section('_DEFAULT'):
            self._cp.add_section('_DEFAULT')
        self._path = _path

    def commit(self, uri=None):
        _path = urlparse(uri, scheme="file://").path if uri else self._path
        with open(_path, 'w') as fp:
            self._cp.write(fp)
        self._path = _path

    def get(self, profile, key):
        _profile = profile.upper()
        _profile = "_DEFAULT" if _profile == "DEFAULT" else _profile
        try:
            return self._cp.get(_profile, key)
        except NoSectionError:
            raise ProfileNotFoundException(
                "Profile '{}' does not exist".format(profile)
            )
        except NoOptionError:
            raise KeyNotFoundException(
                "Key '{}' does not exist in profile '{}'".format(key, profile)
            )

    def set(self, profile, key, value):
        _profile = profile.upper()
        _profile = "_DEFAULT" if _profile == "DEFAULT" else _profile
        try:
            self._cp.set(_profile, key, value)
        except NoSectionError:
            raise ProfileNotFoundException(
                "Profile '{}' does not exist".format(profile)
            )

    def add_profile(self, profile):
        self._cp.add_section(profile.upper())

    def get_profile_dict(self, profile):
        _profile = profile.upper()
        _profile = "_DEFAULT" if _profile == "DEFAULT" else _profile
        return dict(
            [(k, v) for k, v in self._cp.items(_profile) if k != "__ver__"]
        )
