from ConfigParser import SafeConfigParser
from config_gen.adapaters import IniAdapter
from config_gen import Keystore
from os.path import split
from unittest import TestCase
from uuid import uuid4
import tempfile


class TestKeystore(TestCase):
    def setUp(self):
        self._path = tempfile.mktemp(".ini")
        self._ini_uri = "file://{}".format("/".join(split(self._path)))

    def test_create_keystore(self):
        _u = str(uuid4())
        k = Keystore(IniAdapter)
        k.load(self._ini_uri)
        k['test_value'] = _u
        del k

        cp = SafeConfigParser()
        cp.read(self._path)
        self.assertEqual(_u, cp.get("_default", "test_value"))

    def test_undefined_key(self):
        _u = str(uuid4())

        cp = SafeConfigParser()
        cp.read(self._path)
        cp.add_section("_default")
        cp.set("_default", 'test_value', _u)
        with open(self._path, 'w') as fp:
            cp.write(fp)

        k = Keystore(IniAdapter)
        k.load(self._ini_uri)
        self.assertNotIn("bad_key", k)
        self.assertEqual(k['bad_key'], None)

    def test_remove_key(self):
        _u = str(uuid4())
        _u2 = str(uuid4())

        cp = SafeConfigParser()
        cp.read(self._path)
        cp.add_section("_default")
        cp.set("_default", 'test_value1', _u)
        cp.set("_default", 'test_value2', _u2)
        with open(self._path, 'w') as fp:
            cp.write(fp)

        k = Keystore(IniAdapter)
        k.load(self._ini_uri)
        self.assertEqual(k['test_value1'], _u)
        del k['test_value1']

        del k

        k2 = Keystore(IniAdapter)
        k2.load(self._ini_uri)
        self.assertNotIn("test_value1", k2)
        self.assertEqual(k2['test_value2'], _u2)
