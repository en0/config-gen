from keystore_interface import KeystoreInterface
from exception import ProfileNotFoundException, KeyNotFoundException
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from urlparse import urlparse
from os.path import split


class KeystoreIni(KeystoreInterface):
    __VER__ = "ini.0.1"

    @classmethod
    def _clean_profile_name(cls, profile):
        _profile = profile.upper()
        return "_DEFAULT" if _profile == "DEFAULT" else _profile

    def __init__(self, **kwargs):
        super(KeystoreIni, self).__init__("ini")
        self._cp = RawConfigParser(defaults={"__ver__": self.__VER__})
        self._cp.optionxform = str

    @property
    def version(self):
        return self._cp.get("DEFAULT", "__ver__")

    @property
    def uri(self):
        return "file://{}".format("/".join(split(self._path)))

    @property
    def profiles(self):
        _ret = self._cp.sections()
        return ['default' if x == '_DEFAULT' else x.lower() for x in _ret]

    def get_keys(self, profile):
        try:
            _ret = self._cp.options(self._clean_profile_name(profile))
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
        try:
            return self._cp.get(self._clean_profile_name(profile), key)
        except NoSectionError:
            raise ProfileNotFoundException(
                "Profile '{}' does not exist".format(profile)
            )
        except NoOptionError:
            raise KeyNotFoundException(
                "Key '{}' does not exist in profile '{}'".format(key, profile)
            )

    def set(self, profile, key, value):
        try:
            self._cp.set(self._clean_profile_name(profile), key, value)
        except NoSectionError:
            raise ProfileNotFoundException(
                "Profile '{}' does not exist".format(profile)
            )

    def add_profile(self, profile):
        self._cp.add_section(self._clean_profile_name(profile))

    def get_profile_dict(self, profile):
        return dict([
            (k, v)
            for k, v
            in self._cp.items(self._clean_profile_name(profile))
            if k != "__ver__"
        ])
