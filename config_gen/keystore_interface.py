class KeystoreInterface(object):
    __KS_TYPE__ = None

    def __init__(self, ks_type):
        """ Should be called from override """
        self.__KS_TYPE__ = ks_type

    @property
    def ks_type(self):
        return self.__KS_TYPE__

    @property
    def uri(self):
        """ Override """
        raise NotImplemented("Not Implemented")

    @property
    def profiles(self):
        """ Override """
        raise NotImplemented("Not Implemented")

    def get_keys(self, profile):
        """ Override """
        raise NotImplemented("Not Implemented")

    def load(self, uri):
        """ Override """
        raise NotImplemented("Not Implemented")

    def commit(self, uri=None):
        """ Override """
        raise NotImplemented("Not Implemented")

    def get(self, profile, key):
        """ Override """
        raise NotImplemented("Not Implemented")

    def set(self, profile, key, value):
        """ Override """
        raise NotImplemented("Not Implemented")

    def add_profile(self, profile):
        """ Override """
        raise NotImplemented("Not Implemented")

    def get_profile_dict(self, profile):
        """ Override """
        raise NotImplemented("Not Implemented")
