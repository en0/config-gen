from ConfigParser import SafeConfigParser
from config_gen import Keystore
from config_gen.exception import ProfileNotFoundException, KeyNotFoundException
from config_gen.keystore_ini import KeystoreIni
from os.path import split
from unittest import TestCase
from uuid import uuid4
import tempfile


class TestKeystore(TestCase):
    def setUp(self):
        self._path = tempfile.mktemp(".ini")
        self._ini_uri = "file://{}".format("/".join(split(self._path)))

    def test_create_keystore_ini(self):
        ks = Keystore("ini")
        ks.commit(self._ini_uri)
        cp = SafeConfigParser()
        cp.read(self._path)
        self.assertEqual(cp.get("DEFAULT", "__ver__"), KeystoreIni.__VER__)

    def test_read_keystore_ini(self):
        _uuid = str(uuid4())
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format(KeystoreIni.__VER__),
                "[DEVEL]\n",
                "test_key = {}\n".format(_uuid)
            ])

        ks = Keystore("ini")
        ks.load(self._ini_uri)
        self.assertEqual(ks.get("devel", "test_key"), _uuid)

    def test_read_and_modify(self):
        _uuid1 = str(uuid4())
        _uuid2 = str(uuid4())
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format(KeystoreIni.__VER__),
                "[DEVEL]\n",
                "test_key = {}\n".format(_uuid1)
            ])

        ks = Keystore("ini")
        ks.load(self._ini_uri)
        ks.set("devel", "test_key", _uuid2)
        ks.commit()

        ks2 = Keystore("ini")
        ks2.load(self._ini_uri)
        self.assertEqual(ks2.get("devel", "test_key"), _uuid2)

    def test_read_version(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format("abc123"),
                "[DEVEL]",
            ])
        ks = Keystore("ini")
        ks.load(self._ini_uri)
        self.assertEqual(ks.version, "abc123")

    def test_read_and_add_profile(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format(KeystoreIni.__VER__),
                "[DEVEL]",
            ])
        ks = Keystore("ini")
        ks.load(self._ini_uri)
        ks.add_profile("sit")
        ks.commit()

        cp = SafeConfigParser()
        cp.read(self._path)
        self.assertTrue(cp.has_section("SIT"))

    def test_read_bad_profile(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format(KeystoreIni.__VER__),
                "[DEVEL]",
            ])
        ks = Keystore("ini")
        ks.load(self._ini_uri)

        self.assertRaises(
            ProfileNotFoundException,
            ks.get,
            "bad_profile",
            "bad_key"
        )

    def test_read_bad_key(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format(KeystoreIni.__VER__),
                "[DEVEL]",
            ])
        ks = Keystore("ini")
        ks.load(self._ini_uri)
        self.assertRaises(
            KeyNotFoundException,
            ks.get,
            "devel",
            "bad_key"
        )

    def test_write_bad_profile(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "__ver__ = {}\n\n".format(KeystoreIni.__VER__),
                "[DEVEL]",
            ])
        ks = Keystore("ini")
        ks.load(self._ini_uri)
        self.assertRaises(
            ProfileNotFoundException,
            ks.set,
            "bad_profile", "some_key", "some_value"
        )

    def test_bad_type(self):
        self.assertRaises(
            ValueError,
            Keystore,
            ("bad type")
        )
