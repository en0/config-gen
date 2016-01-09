from config_gen import Library, Keystore
from os.path import split
from unittest import TestCase
import tempfile
from ConfigParser import SafeConfigParser
from config_gen.exception import KeystoreExistsException
from config_gen.adapaters import IniAdapter


class TestLibrary(TestCase):

    def setUp(self):
        self._path = tempfile.mktemp(".ini")
        self._ini_path = tempfile.mktemp(".ini")
        self._ini_uri = "file://{}".format("/".join(split(self._ini_path)))

    def test_create_library(self):
        lib = Library(self._path)
        _cp = SafeConfigParser()
        _cp.read(self._path)
        # If it didn't error, it worked
        self.assertIsInstance(lib, Library)

    def test_create_library_and_add_keystore(self):
        lib = Library(self._path)
        lib.add_keystore("default", "ini", self._ini_uri)
        lib.save()

        _cp = SafeConfigParser()
        _cp.read(self._path)
        self.assertEqual(_cp.get("_DEFAULT", "uri"), self._ini_uri)

    def test_read_library(self):
        ks = Keystore(IniAdapter)
        ks.load(self._ini_uri)
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[_DEFAULT]\n",
                "type = {}\n".format(ks.ks_type),
                "uri = {}\n".format(ks.uri),
            ])
        lib = Library(self._path)
        ks1 = lib.get_keystore("default")
        self.assertEqual(ks1.ks_type, ks.ks_type)
        self.assertEqual(ks1.uri, ks.uri)
        self.assertEqual(self._ini_uri, ks1.uri)

    def test_add_keystore(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[_DEFAULT]\n",
            ])

        lib = Library(self._path)
        lib.add_keystore("my_store", "ini", self._ini_uri)
        lib.save()

        _cp = SafeConfigParser()
        _cp.read(self._path)
        self.assertEqual(_cp.get("MY_STORE", "uri"), self._ini_uri)

    def test_load_keystore_from_cache(self):
        lib = Library(self._path)
        ks = Keystore(IniAdapter)
        ks.load(self._ini_uri)
        lib.add_keystore("my_store", "ini", self._ini_uri)
        ks1 = lib.get_keystore("my_store")
        ks2 = lib.get_keystore("my_store")
        self.assertIs(ks2, ks1)

    def test_add_existing_keystore(self):
        lib = Library(self._path)
        lib.add_keystore("my_store", "ini", self._ini_uri)
        self.assertRaises(
            KeystoreExistsException,
            lib.add_keystore,
            "my_store", None, None
        )

    def test_list_stores(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[STORE1]\n",
                "[STORE2]\n",
                "[STORE3]\n",
            ])

        lib = Library(self._path)
        self.assertListEqual(["store1", "store2", "store3"], lib.stores)

    def test_list_stores_with_default(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[_DEFAULT]\n",
                "type = ini\n",
                "uri = /dev/null\n",
                "[STORE1]\n",
                "[STORE2]\n",
                "[STORE3]\n",
            ])

        lib = Library(self._path)
        self.assertListEqual([
            "default",
            "store1",
            "store2",
            "store3"
        ], lib.stores)

    def test_read_file_pointer(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[_DEFAULT]\n",
                "[STORE1]\n",
                "[STORE2]\n",
                "[STORE3]\n",
            ])

        with open(self._path, 'r') as fid:
            lib = Library(fp=fid)
            self.assertListEqual(["default", "store1", "store2", "store3"], lib.stores)
